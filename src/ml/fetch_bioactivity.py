import os
import time
import requests
import pandas as pd
import io
import zipfile

class HttpFile:
    """A file-like object that streams a remote file via HTTP Range requests."""
    def __init__(self, url):
        self.url = url
        r = requests.head(url, timeout=10)
        r.raise_for_status()
        self.size = int(r.headers.get('content-length', 0))
        self.pos = 0

    def seek(self, offset, whence=0):
        if whence == 0:
            self.pos = offset
        elif whence == 1:
            self.pos += offset
        elif whence == 2:
            self.pos = self.size + offset
        return self.pos

    def tell(self):
        return self.pos

    def read(self, size=-1):
        if size == -1 or size > self.size - self.pos:
            size = self.size - self.pos
        if size == 0:
            return b""
        end_pos = self.pos + size - 1
        headers = {"Range": f"bytes={self.pos}-{end_pos}"}
        
        for attempt in range(3):
            try:
                r = requests.get(self.url, headers=headers, timeout=15)
                r.raise_for_status()
                data = r.content
                self.pos += len(data)
                return data
            except Exception as e:
                if attempt == 2:
                    raise e
                time.sleep(2)

    def close(self):
        pass
    
    def seekable(self):
        return True

def fetch_with_retry(url, retries=2, timeout=10):
    """Fetch URL with basic retry and timeout logic."""
    for attempt in range(retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                return response
            else:
                print(f"Request failed: {url} with status {response.status_code}")
                if attempt == retries:
                    return None
        except requests.exceptions.RequestException as e:
            print(f"Request error on {url}: {e}")
            if attempt == retries:
                return None
        
        print(f"Retrying ({attempt + 1}/{retries})...")
        time.sleep(2)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    data_raw_dir = os.path.join(project_root, 'data', 'raw')
    os.makedirs(data_raw_dir, exist_ok=True)
    
    aid = 1706
    concise_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/concise/CSV"
    
    print(f"Attempting concise endpoint: {concise_url}")
    response = fetch_with_retry(concise_url, retries=2, timeout=10)
    
    if response and response.status_code == 200:
        print("Concise endpoint succeeded.")
        concise_output_path = os.path.join(data_raw_dir, f'mpro_pubchem_aid{aid}_concise.csv')
        
        with open(concise_output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"Saved concise data to {concise_output_path}")
        
        try:
            df = pd.read_csv(io.StringIO(response.text), low_memory=False)
            print("\n--- Columns found in Concise CSV ---")
            for col in df.columns:
                print(f" - {col}")
            print("------------------------------------\n")
            
            total_records = len(df)
            print(f"Total row count: {total_records}")
            print("Stopping execution (concise endpoint was successful and didn't require fallback).")
            return
        except Exception as e:
            print(f"Failed to parse concise CSV: {e}")
            # fall through to zip streaming
            
    print("\nConcise endpoint failed or could not be parsed.")
    print("Falling back to HTTP Range streaming for the bulk zip file...")
    
    zip_url = "https://ftp.ncbi.nlm.nih.gov/pubchem/Bioassay/CSV/Data/0001001_0002000.zip"
    
    try:
        remote_zip = HttpFile(zip_url)
        with zipfile.ZipFile(remote_zip) as z:
            match = None
            for name in z.namelist():
                if name.endswith("1706.csv") or name.endswith("1706.csv.gz"):
                    match = name
                    break
                    
            if not match:
                print("Could not find a matching 1706.csv file in the zip archive.")
                print("Zip file members (first 20):")
                for name in z.namelist()[:20]:
                    print(" -", name)
                raise FileNotFoundError(f"1706.csv not found in {zip_url}")
                
            print(f"Found {match} in the remote zip file. Extracting...")
            
            raw_output_path = os.path.join(data_raw_dir, os.path.basename(match))
            with z.open(match) as zf, open(raw_output_path, 'wb') as f:
                f.write(zf.read())
                
            print(f"Saved extracted file to {raw_output_path}")
            
            print(f"Loading {raw_output_path} as CSV...")
            df = pd.read_csv(raw_output_path, low_memory=False)
            
            print("\n--- Columns found in extracted CSV ---")
            for col in df.columns:
                print(f" - {col}")
            print("--------------------------------------\n")
            
            total_records = len(df)
            print(f"Total row count: {total_records}")
            
    except Exception as e:
        print(f"Zip streaming fallback failed: {e}")
        raise e

if __name__ == "__main__":
    main()
