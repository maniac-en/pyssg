![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/maniac-en/pyssg/pytest.yml)

# pyssg

- `pyssg` is a toy-project written in Python (v3.10.12) implementing the functionality like a [SSG](https://en.wikipedia.org/wiki/Static_site_generator).
- Note: It's not aimed to support the entire markdown syntax. It supports following:

    - Multiline markdown blocks should be separated by newlines:<br><br>
    ```
    - Headings (1-6)
    - Paragraphs
    - Quoteblocks
    - Codeblocks
    - Ordered Lists
    - Unordered Lists
    ```

    - Inline blocks:<br><br>
    ```
    - Bold      -> **bold**
    - Italic    -> _italic_
    - Codeblock -> `code`
    - Link      -> [text](link)
    - Image     -> ![alt-text](src-link)
    ```

  - Nested blocks will throw `ValueError` for `Invalid Markdown Syntax`

- It serves the generated site using a TCP server whilst also supporting **hot-reloading** using out-of-the-box python libraries.

    https://github.com/user-attachments/assets/3c66bab4-8fda-4dd5-aad0-924acdffb8fa

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Technical Details](#technical-details)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/maniac-en/pyssg.git
    cd pyssg
    ```

2. Create a virtual environment: (if you want to do testing, else skip this)
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies: (if you want to do testing, else skip this)
    ```bash
    pip install -r requirements.txt
    ```

## Usage

> Note: Not tested on `Windows`

To generate the static site and start the server, run:
```bash
./main.sh
```

## Testing

1. Install pytest:

  - Using `pip`:

  ```bash
  pip install pytest
  ```

  - Or, install from requirements.txt:

  ```bash
  pip install -r requirements.txt
  ```

2. Run the tests:

```bash
./test.sh
```

## Technical Details

### Flow
1. It generates the `HTML` files for `markdown` files present in `/content` directory using `template.html` and static contents such as CSS, Images from `/src/static`.
2. Required files and their filestamps are stored before the server starts so it can check for file changes for hot-reloading.
3. Generated site is stored into `/public` folder which is then served via TCP server
4. Every generated HTML page has a function which calls `/check_update` endpoint on the TCP server every second, server validates if something changed:
  - If yes, it'll regenerate the site and refresh the page that asked to check the update!
  - Logging is disabled for the this because it happens every second and would simply clutter the logs.

### Libraries used
- Using `socketserver` library for the TCP server along with `SimpleHTTPRequestHandler` as the handler.
- `os`, `shutil`, `glob` for file-related utilities.
- `re` for parsing some parts of markdown file.
- `unittest` and `pytest` for testing, including mock-testing. (~160 tests)
- `typing` for type-hints.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
