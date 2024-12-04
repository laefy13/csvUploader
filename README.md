# Backend API with Python Background Service

## Installation
- Python version
   - 3.10
- Clone project

```bash
  git clone https://github.com/laefy13/csvUploader
```
## Dependencies
- Install libraries
   ```
      pip install -r requirements.txt
   ```
- .env file that contains the MongoDb connection string is also needed, there is a template named template.env
## How to use
 - To run the API backend
   ```
      cd api
   ```
   ```
      fastapi dev main.py
   ```
 - To run the Background service
   ```
      cd service
   ```
   ```
      python main.py --workers <num_workers>
   ```

## Assumptions
 - The /aggregated_stats/event endpoint will send back 10 groups "event", "discipline", and "event_date", with other data.
 - The files in storage/app/medialists won't be manually handled by anyone.
 - The maximum file size will only be 50mb


