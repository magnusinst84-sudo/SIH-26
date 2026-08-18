import pandas as pd
import numpy as np
import requests
import time
import sys
import os

def main():
    input_csv = "data/raw/mpro_pubchem_aid1706_concise.csv"
    output_csv = "data/raw/mpro_labeled_smiles.csv"
    
    print(f"Loading data from {input_csv}...")
    df = pd.read_csv(input_csv)
    
    # 1. Drop rows with missing or null CID
    initial_rows = len(df)
    df = df.dropna(subset=['CID'])
    df['CID'] = df['CID'].astype(int)
    print(f"Dropped {initial_rows - len(df)} rows with missing or null CID.")

    # 3. Drop rows where Activity Outcome is 'Inconclusive' or 'Unspecified'
    # It is best to do this before duplicate checking so that an 'Inconclusive' 
    # record doesn't falsely create a conflict with a valid 'Active'/'Inactive' record.
    valid_outcomes = ['Active', 'Inactive']
    df['Activity Outcome'] = df['Activity Outcome'].str.strip().str.capitalize()
    df = df[df['Activity Outcome'].isin(valid_outcomes)]
    
    # 2. Check for duplicate CIDs
    # If all 'Activity Outcome' values agree, collapse to one row
    # If they conflict, drop that CID entirely and count it as "conflicting, dropped"
    outcome_nunique = df.groupby('CID')['Activity Outcome'].nunique()
    conflicting_cids = outcome_nunique[outcome_nunique > 1].index
    conflict_count = len(conflicting_cids)
    
    # Drop conflicting CIDs
    df = df[~df['CID'].isin(conflicting_cids)]
    
    # Collapse agreeing duplicates to one row (take the first occurrence)
    df = df.groupby('CID').first().reset_index()
    
    # 4. Print totals
    total_unique_cids = len(df)
    active_count = len(df[df['Activity Outcome'] == 'Active'])
    inactive_count = len(df[df['Activity Outcome'] == 'Inactive'])
    
    print(f"Total unique CIDs after dedup: {total_unique_cids}")
    print(f"Count of CIDs dropped for conflicts: {conflict_count}")
    print(f"Final Active count: {active_count}")
    print(f"Final Inactive count: {inactive_count}")
    
    # 5. Subsample
    df_active = df[df['Activity Outcome'] == 'Active']
    df_inactive = df[df['Activity Outcome'] == 'Inactive']
    
    target_inactive = active_count * 4
    if len(df_inactive) < target_inactive:
        print(f"WARNING: Available Inactives ({len(df_inactive)}) is less than 4x Actives ({target_inactive}). Keeping all Inactives.")
        df_inactive_sampled = df_inactive
    else:
        df_inactive_sampled = df_inactive.sample(n=target_inactive, random_state=42)
        
    df_sampled = pd.concat([df_active, df_inactive_sampled]).reset_index(drop=True)
    
    # 6. Fetch CanonicalSMILES from PubChem PUG-REST
    cids_to_fetch = df_sampled['CID'].tolist()
    print(f"\nRows going into SMILES lookup: {len(cids_to_fetch)}")
    
    batch_size = 100
    smiles_results = []
    
    for i in range(0, len(cids_to_fetch), batch_size):
        batch_cids = cids_to_fetch[i:i+batch_size]
        cids_str = ",".join(map(str, batch_cids))
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cids_str}/property/CanonicalSMILES/CSV"
        
        max_retries = 2
        success = False
        
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Parse CSV response: CID,CanonicalSMILES
                    lines = response.text.strip().split('\n')
                    if len(lines) > 1:
                        for line in lines[1:]: # Skip header
                            parts = line.split(',')
                            if len(parts) >= 2:
                                cid_val = parts[0].strip(' "')
                                smiles_val = parts[1].strip(' "')
                                smiles_results.append({'CID': int(cid_val), 'smiles': smiles_val})
                    success = True
                    break
                else:
                    print(f"Batch {i//batch_size} (CIDs {batch_cids[0]}-{batch_cids[-1]}) failed with status code {response.status_code}. Attempt {attempt+1}/{max_retries+1}")
            except requests.exceptions.RequestException as e:
                print(f"Batch {i//batch_size} request failed: {e}. Attempt {attempt+1}/{max_retries+1}")
                
            if attempt < max_retries:
                time.sleep(1) # wait before retry
                
        if not success:
            print(f"\nCRITICAL ERROR: Failed to fetch SMILES for batch starting at index {i} after {max_retries+1} attempts.")
            print(f"Failing CID batch: {batch_cids}")
            print(f"Last status code: {response.status_code if 'response' in locals() else 'Connection Error'}")
            sys.exit(1)
            
        time.sleep(0.3) # 0.3s delay between batches
        
    df_smiles = pd.DataFrame(smiles_results)
    
    # 7. Merge SMILES back by CID
    if not df_smiles.empty:
        df_final = pd.merge(df_sampled, df_smiles, on='CID', how='inner')
    else:
        df_final = pd.DataFrame(columns=df_sampled.columns.tolist() + ['smiles'])
        
    resolved_count = len(df_final)
    failed_resolution_count = len(cids_to_fetch) - resolved_count
    
    # 8. Save final result to data/raw/mpro_labeled_smiles.csv
    df_final['compound_id'] = 'CID-' + df_final['CID'].astype(str)
    
    # Ensure correct column name for Activity Value
    activity_val_col = 'Activity Value [uM]' if 'Activity Value [uM]' in df_final.columns else 'Activity Value'
    
    df_export = pd.DataFrame({
        'compound_id': df_final['compound_id'],
        'smiles': df_final['smiles'],
        'activity_label': df_final['Activity Outcome'].str.lower(),
        'activity_value_um': df_final[activity_val_col] if activity_val_col in df_final.columns else np.nan
    })
    
    # Ensure directory exists just in case
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_export.to_csv(output_csv, index=False)
    
    # 9. Print final summary
    final_active = len(df_export[df_export['activity_label'] == 'active'])
    final_inactive = len(df_export[df_export['activity_label'] == 'inactive'])
    
    print(f"\nSaved final dataset to {output_csv}")
    print(f"\n--- Final Summary ---")
    print(f"Rows going into SMILES lookup: {len(cids_to_fetch)}")
    print(f"Rows successfully resolved: {resolved_count}")
    print(f"Rows dropped for failed resolution: {failed_resolution_count}")
    print(f"Final active count: {final_active}")
    print(f"Final inactive count: {final_inactive}")
    
    if final_inactive > 0:
        ratio = final_active / final_inactive
        if ratio < 1:
            print(f"Active:Inactive ratio: 1 : {1/ratio:.2f}")
        else:
            print(f"Active:Inactive ratio: {ratio:.2f} : 1")
    else:
        print("Active:Inactive ratio: undefined (no inactives)")

if __name__ == "__main__":
    main()
