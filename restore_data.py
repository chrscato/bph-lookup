import sqlite3
import json

def restore_data():
    # Connect to the database
    conn = sqlite3.connect('compensation_rates.db')
    cursor = conn.cursor()
    
    # Load the backup data
    with open('database_backup.json', 'r') as f:
        data = json.load(f)
    
    # Table name mapping (old name -> new name)
    table_mapping = {
        'state': 'core_state',
        'region': 'core_region',
        'procedure_code': 'core_procedurecode',
        'fee_schedule': 'core_feeschedule',
        'fee_schedule_rate': 'core_feeschedulerate',
        'medicare_locality_map': 'core_medicarelocalitymap',
        'medicare_locality_meta': 'core_medicarelocalitymeta',
        'cms_gpci': 'core_cmsgpci',
        'cms_rvu': 'core_cmsrvu',
        'cms_conversion_factor': 'core_cmsconversionfactor'
    }
    
    # For each table in the backup
    for old_table_name, table_data in data.items():
        if old_table_name != 'django_migrations':  # Skip Django's migration table
            # Get the new table name
            new_table_name = table_mapping.get(old_table_name, old_table_name)
            
            columns = table_data['columns']
            rows = table_data['rows']
            
            if rows:  # Only restore if there's data
                try:
                    # Create the INSERT statement
                    placeholders = ','.join(['?' for _ in columns])
                    insert_sql = f"INSERT INTO {new_table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    
                    # Insert the data
                    cursor.executemany(insert_sql, rows)
                    print(f"Restored data to {new_table_name}")
                except sqlite3.OperationalError as e:
                    print(f"Error restoring {new_table_name}: {str(e)}")
    
    conn.commit()
    conn.close()
    print("Data restoration completed!")

if __name__ == "__main__":
    print("Starting data restoration...")
    restore_data()
    print("Process completed!") 