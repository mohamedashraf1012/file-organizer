import sys
sys.path.insert(0, '.')
from src.organizer import organize_files, get_folder_stats

stats = get_folder_stats('test_data')
print('Stats before:', stats)

summary = organize_files('test_data', dry_run=True)
print(f"Dry run: {summary['moved']} files simulated | {summary['errors']} errors")
assert summary['errors'] == 0, 'Headless validation failed!'
print('Headless validation passed!')