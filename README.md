# [CSD-Code-Sample-Dataset](https://github.com/Cafeo-Group/MCSCMD-Multi-Code-Sample-Commit-Message-Dataset)

This repository provides a complete pipeline to collect and store data from  **345 curated code sample repositories** . By executing the Jupyter notebooks provided in the `notebook/` directory, you can store structured data locally in a **PostgreSQL** database, enabling analysis and research on the evolution of code samples software.

## Dataset Overview

The collected data is organized across the following relational tables:

* **Ecosystems** – Software development ecosystems (e.g., Spring, AWS, Azure).
* **Organizations** – GitHub organizations owning the repositories.
* **Repositories** – Basic data of each repository.
* **Commits** – Data such as sha, message and timestamp.
* File - General data of files of repositories, such as name and type.
* **Commit Files** – File's data that is from specific commits
* **Hunks** – Code-level changes (diffs) between commit versions.

## Usage

To create the dataset locally:

1. Intall PostgreSQL in your machine.
2. Clone this repository.
3. Insert your local postgres database password in a `.env` (see `.env.example`).
4. Navigate to the `notebook/` folder.
5. Execute the notebooks  **in the following order**:
   * `0_setup.ipynb`
   * `1_ecosystems.ipynb`
   * `2_organizations.`ipynb
   * `3_repositories.ipynb`
   * `4_commits.ipynb`
   * `5_files.ipynb`
   * `6_cfs.ipynb`
   * `7_hunks.ipynb`

> **Total runtime** : Between **4 to 7 hours** depending on your system. Basic data (from ecosystems to files) is usually available within 10 minutes.

## Notes

* To extract the data repositories are cloned in *bare* mode, reducing storage the needed.
* The resulting database is approximately **1.5 GB** in size.
* Most of the Jupyter notebook files use 100% of CPU resources for optimized multi-threading.
* You can customize the `playground.py` file to get data from repositories without processing the full dataset.

## Database Documentation

[ER Diagram](https://lucid.app/lucidchart/27e83443-34d9-4538-a3d3-6065fe012db5/edit?viewport_loc=3483%2C2013%2C2422%2C1248%2C0_0&invitationId=inv_76afb91f-45b5-4d97-bb0a-fc5b6910b2cf)
