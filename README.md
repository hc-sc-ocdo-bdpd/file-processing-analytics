# file-processing-analytics

**file-processing-analytics** is a Python library designed for analyzing and gathering metadata from a collection of files. It seamlessly integrates with the `file-processing` suite, enabling efficient metadata extraction and storage in CSV format. This library is ideal for data discovery, auditing, and understanding the contents of file directories or file lists.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Extending the Library](#extending-the-library)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

- **Directory and List Input Support**: Accepts file input via directories (with optional recursive search) or predefined lists of file paths.
- **Metadata Extraction**: Leverages the `file-processing` library to gather metadata from each file.
- **Error Logging**: Captures processing errors per file, logging them into the CSV output for easy diagnostics.
- **Progress Tracking**: Supports tracking of processed files to resume long-running tasks, using SQLite.
- **Output to CSV**: Aggregates results in a CSV format, making it easy to view, share, or further analyze.

---

## Installation

Install `file-processing-analytics` via GitHub:

```bash
pip install git+https://github.com/hc-sc-ocdo-bdpd/file-processing-analytics.git
```

---

## Quick Start

Here’s how to start using `file-processing-analytics`:

```python
from file_processing_analytics import AnalyticsProcessor

# Initialize an AnalyticsProcessor
processor = AnalyticsProcessor(
    input_collection="path/to/directory",
    output_csv_path="output/results.csv"
)

# Process files and save metadata to CSV
processor.process_files()
```

### Using List Inputs

Alternatively, provide a list of file paths for processing:

```python
file_list = ["file1.pdf", "file2.docx", "file3.jpg"]
processor = AnalyticsProcessor(input_collection=file_list, output_csv_path="output/results.csv")
processor.process_files()
```

---

## Architecture

### Key Components

- **AnalyticsProcessor**: Core class that orchestrates metadata extraction and error handling.
- **Input Collections**: Supports both `DirectoryInput` (for directories) and `ListInput` (for custom file lists).
- **ProgressTracker**: Utilizes SQLite to keep track of processed files, ensuring resiliency in case of interruptions.

### Error Handling

Errors encountered during processing are logged directly into the CSV file, capturing both the file name and the error description.

---

## Extending the Library

You can customize or extend functionality by creating custom InputCollections or by adding new processing behaviors in conjunction with `file-processing`.

---

## Contributing

We welcome contributions! To get involved:

1. **Fork the repository**: Create your own fork on GitHub.
2. **Create a feature branch**: Work on your feature or bug fix in a new branch.
3. **Write tests**: Ensure your changes are thoroughly tested.
4. **Submit a Pull Request**: When ready, submit a PR for review.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contact

For questions, support, or collaboration inquiries:

- **Email**: [ocdo-bdpd@hc-sc.gc.ca](mailto:ocdo-bdpd@hc-sc.gc.ca)

---

*Empowering data discovery and metadata analysis. Explore our repository or contribute to enhance its capabilities!*