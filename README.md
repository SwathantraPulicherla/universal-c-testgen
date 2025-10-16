# Universal C Test Generator

🚀 **Complete AI-powered C testing pipeline - Generate, Execute, and Analyze Coverage**

## Quick Start
```bash
# 1. Install
git clone https://github.com/your-username/universal-c-testgen
cd universal-c-testgen
pip install -e .

# 2. Set API key
export GEMINI_API_KEY="your-google-ai-studio-key"

# 3. Generate, run tests, and get coverage for ANY C repo
c-testgen /path/to/your/c/project --coverage
```

## Features
✅ **AI Test Generation** - Uses Gemini 2.5 Pro to create comprehensive Unity tests  
✅ **Automatic Test Execution** - Compiles and runs all generated tests  
✅ **Coverage Analysis** - Generates detailed HTML coverage reports  
✅ **Repository Agnostic** - Works with ANY C project structure  
✅ **Zero Configuration** - No manual tuning needed  
✅ **Unity Framework Integration** - Downloads and sets up Unity automatically  
✅ **GitHub Actions Ready** - Complete CI/CD workflow included  

## 🆕 Smart Processing Architecture

The generator now uses intelligent file-by-file processing:

1. **Global Dependency Mapping**: Scans entire repository to map all functions
2. **Targeted File Analysis**: Processes each file individually with exact stub requirements  
3. **Smart Stub Generation**: Knows exactly which functions need stubs based on global context
4. **No Context Overload**: Each API call gets only the relevant file content

## Usage Examples

### Basic Test Generation
```bash
c-testgen /path/to/repo
# Generates tests in tests/generated/
```

### Generate + Execute Tests
```bash
c-testgen /path/to/repo --run-tests
# Generates tests and runs them immediately
```

### Full Pipeline (Generate + Execute + Coverage)
```bash
c-testgen /path/to/repo --coverage
# Complete testing pipeline with coverage reports
```

### Custom Output Directory
```bash
c-testgen /path/to/repo --output my_tests --coverage
```

## What You Get

### 🤖 AI-Generated Tests
- **Comprehensive test suites** for all functions
- **Boundary value testing** for edge cases
- **Error condition handling**
- **Mock/stub generation** for dependencies
- **Unity framework integration**

### 🧪 Automatic Test Execution
- **GCC compilation** with coverage flags
- **Unity framework setup** (auto-downloaded)
- **Test result collection** and reporting
- **Pass/fail status** for each test suite

### 📊 Coverage Reports
- **HTML coverage reports** (via lcov/genhtml)
- **Line-by-line coverage** analysis
- **Function coverage** metrics
- **Branch coverage** information
- **Interactive web interface**

## Output Structure
```
your-repo/
├── tests/
│   └── generated/
│       ├── test_file1.c    # AI-generated Unity tests
│       └── test_file2.c    # AI-generated Unity tests
├── build/
│   ├── test_file1_runner   # Compiled test executables
│   └── test_file2_runner   # Compiled test executables
├── coverage_report/
│   ├── index.html         # Main coverage report
│   └── *.html            # Detailed file reports
├── test_results.txt       # Test execution summary
└── coverage.info         # Raw coverage data
```

## Requirements
- **Python 3.8+**
- **GCC compiler**
- **lcov** (for coverage reports)
- **Gemini API key** (free from Google AI Studio)

## Get Your Free API Key
1. Visit https://aistudio.google.com/
2. Sign in with Google account
3. Create API key
4. Set environment variable: `export GEMINI_API_KEY="your-key"`

## GitHub Actions Integration

The package includes a complete GitHub Actions workflow that:
- Triggers on push/PR
- Generates tests with Gemini
- Executes all tests
- Generates coverage reports
- Commits results back to repository
- Deploys coverage to GitHub Pages

## Advanced Usage

### Programmatic Usage
```python
from universal_c_testgen import CTestGenerator

generator = CTestGenerator(api_key="your-key")
generator.generate_tests("/path/to/repo")
generator.run_tests()
generator.generate_coverage()
```

### Custom Test Templates
Extend the `templates/` directory with custom Unity test templates.

## Supported C Constructs
- ✅ Functions with any signature
- ✅ Global variables
- ✅ Struct types
- ✅ Pointer operations
- ✅ Standard library functions
- ✅ Header file dependencies

## Limitations
- C code must be compilable with GCC
- External library dependencies need manual setup
- Complex preprocessor macros may need special handling

---

**Made with ❤️ for C developers who want comprehensive testing without the hassle**

### Basic Test Generation
```bash
c-testgen /path/to/repo
# Generates tests in tests/generated/
```

### Generate + Execute Tests
```bash
c-testgen /path/to/repo --run-tests
# Generates tests and runs them immediately
```

### Full Pipeline (Generate + Execute + Coverage)
```bash
c-testgen /path/to/repo --coverage
# Complete testing pipeline with coverage reports
```

### Custom Output Directory
```bash
c-testgen /path/to/repo --output my_tests --coverage
```

## What You Get

### 🤖 AI-Generated Tests
- **Comprehensive test suites** for all functions
- **Boundary value testing** for edge cases
- **Error condition handling**
- **Mock/stub generation** for dependencies
- **Unity framework integration**

### 🧪 Automatic Test Execution
- **GCC compilation** with coverage flags
- **Unity framework setup** (auto-downloaded)
- **Test result collection** and reporting
- **Pass/fail status** for each test suite

### 📊 Coverage Reports
- **HTML coverage reports** (via lcov/genhtml)
- **Line-by-line coverage** analysis
- **Function coverage** metrics
- **Branch coverage** information
- **Interactive web interface**

## Output Structure
```
your-repo/
├── tests/
│   └── generated/
│       ├── test_file1.c    # AI-generated Unity tests
│       └── test_file2.c    # AI-generated Unity tests
├── build/
│   ├── test_file1_runner   # Compiled test executables
│   └── test_file2_runner   # Compiled test executables
├── coverage_report/
│   ├── index.html         # Main coverage report
│   └── *.html            # Detailed file reports
├── test_results.txt       # Test execution summary
└── coverage.info         # Raw coverage data
```

## Requirements
- **Python 3.8+**
- **GCC compiler**
- **lcov** (for coverage reports)
- **Gemini API key** (free from Google AI Studio)

## Get Your Free API Key
1. Visit https://aistudio.google.com/
2. Sign in with Google account
3. Create API key
4. Set environment variable: `export GEMINI_API_KEY="your-key"`

## GitHub Actions Integration

The package includes a complete GitHub Actions workflow that:
- Triggers on push/PR
- Generates tests with Gemini
- Executes all tests
- Generates coverage reports
- Commits results back to repository
- Deploys coverage to GitHub Pages

## Advanced Usage

### Programmatic Usage
```python
from universal_c_testgen import CTestGenerator

generator = CTestGenerator(api_key="your-key")
generator.generate_tests("/path/to/repo")
generator.run_tests()
generator.generate_coverage()
```

### Custom Test Templates
Extend the `templates/` directory with custom Unity test templates.

## Supported C Constructs
- ✅ Functions with any signature
- ✅ Global variables
- ✅ Struct types
- ✅ Pointer operations
- ✅ Standard library functions
- ✅ Header file dependencies

## Limitations
- C code must be compilable with GCC
- External library dependencies need manual setup
- Complex preprocessor macros may need special handling

---

**Made with ❤️ for C developers who want comprehensive testing without the hassle**