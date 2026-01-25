# Datasets Directory

This directory contains versioned datasets managed by DVC.

## Structure

Each dataset should be organized in its own subdirectory:

```
datasets/
  kidney_textures/
    train/
      image001.jpg
      image002.jpg
    test/
      image003.jpg
  gallbladder_textures/
    ...
```

## Important Notes

- **Dataset files are NOT tracked by Git** - they are managed by DVC
- **DVC tracks metadata** (.dvc files) which are committed to Git
- **Physical data is stored** in Azure Blob Storage
- **Dataset versions** are tied to Git commits

## Workflow

1. Add/modify data in `datasets/<dataset_id>/`
2. Run `python -m mlops_lineage dataset push --dataset-id <id> --message "..."`
3. DVC creates/updates `.dvc` file and pushes data to Azure
4. Git commits the `.dvc` metadata file
5. Git commit hash becomes the dataset version

## Reproducibility

To retrieve the exact dataset used by a model:
```powershell
python -m mlops_lineage model pull-data --model-name my_model --model-version 1
```

This will:
1. Read model tags to get dataset_id and dataset_version (git commit)
2. Create a git worktree at that commit
3. Run `dvc pull` in the worktree
4. Print the path to the exact dataset
