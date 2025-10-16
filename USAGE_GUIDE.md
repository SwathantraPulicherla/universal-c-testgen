# Universal C Test Generator - Complete Usage Guide

## Overview
The Universal C Test Generator is an AI-powered tool that automatically generates Unity unit tests for any C repository using Google's Gemini AI. This guide provides step-by-step instructions for using the tool on new C repositories.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Git**: For cloning repositories
- **Internet connection**: For AI API calls
- **GCC compiler**: For test compilation (optional, for full workflow)

### API Requirements
- **Google Gemini API key**: Obtain from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **API credits**: Ensure sufficient credits for AI calls

## Installation

### Step 1: Clone the Tool Repository
```bash
git clone https://github.com/SwathantraPulicherla/universal-c-testgen.git
cd universal-c-testgen
```

### Step 2: Install Dependencies
```bash
pip install -e .
```

### Step 3: Verify Installation
```bash
c-testgen --help
```
Expected output: Shows help information for the c-testgen command.

## API Configuration

### Option 1: Environment Variable (Recommended)
```bash
export GEMINI_API_KEY="your-actual-api-key-here"
```

### Option 2: .env File
Create a `.env` file in your working directory:
```
GEMINI_API_KEY=your-actual-api-key-here
```

### Testing API Connection
```bash
python -c "import google.generativeai as genai; genai.configure(api_key='your-key'); print('API configured successfully')"
```

## Using on a New C Repository

### Step 1: Obtain the Target Repository
```bash
# Clone the repository you want to test
git clone https://github.com/developer/their-c-repo.git
cd their-c-repo
```

### Step 2: Examine Repository Structure
```bash
# Check for C files
find . -name "*.c" -o -name "*.h" | head -10

# Look at the overall structure
tree . -I '__pycache__|*.o|*.exe' | head -20
```

**Expected structure**: Look for `.c` source files and `.h` header files.

### Step 3: Run the Test Generator
```bash
# Basic usage - generates tests in target repo
c-testgen /full/path/to/their-c-repo

# Example with absolute path
c-testgen /home/user/projects/their-c-repo
```

### Step 4: Monitor Progress
The tool will show progress like:
```
🚀 Starting SMART test generation for: /path/to/repo
� Building global dependency map...
   Mapped X functions across Y files
� Processing Z files...
   🎯 Generating tests for: filename.c
   📋 filename.c: N functions, M need stubs
   ✅ Generated: test_filename.c
🎉 COMPLETED: Z/Z files successfully generated
� Test files saved to: /path/to/repo/tests/generated/
```

## Verification

### Step 1: Check Generated Tests
```bash
# Navigate to the target repository
cd /path/to/their-c-repo

# Check the generated tests directory
ls -la tests/generated/

# Examine a generated test file
head -50 tests/generated/test_filename.c
```

### Step 2: Verify Test Structure
Each generated test file should contain:
- Unity framework includes
- setUp() and tearDown() functions
- Test functions with TEST_ASSERT_* macros
- Stub functions for dependencies
- Proper C syntax and formatting

### Step 3: Test Compilation (Optional)
```bash
# Try compiling the generated tests
gcc -I/path/to/unity/include tests/generated/test_*.c source_files.c -o test_runner
```

## Demo Preparation

### For Presentation

#### 1. Repository Showcase
- Show the tool's GitHub repository
- Demonstrate the AI-generated test examples
- Highlight the smart dependency analysis

#### 2. Live Demo Steps
1. **Show a C repository** (before testing)
2. **Run the tool**: `c-testgen /path/to/repo`
3. **Show results**: Navigate to `tests/generated/`
4. **Explain output**: Point out AI-generated test cases
5. **Highlight features**: Unity integration, stub generation, coverage

#### 3. Key Talking Points
- **AI-Powered**: Uses Gemini 2.0 for intelligent test generation
- **Repository Agnostic**: Works on any C codebase
- **Smart Processing**: File-by-file analysis with dependency mapping
- **Unity Framework**: Industry-standard unit testing
- **Automatic Stubs**: Handles function dependencies automatically

## Troubleshooting

### Common Issues

#### 1. "No C files found"
**Cause**: Repository doesn't contain `.c` files or they're in unexpected locations
**Solution**:
```bash
find /path/to/repo -name "*.c"  # Locate C files
c-testgen /correct/path/to/repo
```

#### 2. "API key not found"
**Cause**: GEMINI_API_KEY not set
**Solution**:
```bash
export GEMINI_API_KEY="your-key"
# OR
echo "GEMINI_API_KEY=your-key" > .env
```

#### 3. "Permission denied" on push
**Cause**: GitHub token lacks permissions
**Solution**: Update token permissions in GitHub settings

#### 4. "Module not found" errors
**Cause**: Tool not properly installed
**Solution**:
```bash
cd universal-c-testgen
pip install -e .
```

### Performance Tips

#### Large Repositories
- The tool processes files individually to avoid context limits
- Large codebases may take longer due to AI API calls
- Monitor progress output for current status

#### API Rate Limits
- Gemini API has rate limits
- For large repositories, consider batch processing
- Monitor API usage in Google AI Studio

## Advanced Usage

### Custom Output Directory
```bash
c-testgen /path/to/repo --output custom/test/dir
```

### Specific File Processing
The tool automatically finds all C files. For manual control, ensure files are in standard locations.

### Integration with CI/CD
The generated tests can be integrated into:
- GitHub Actions
- Jenkins pipelines
- Local build systems

## File Structure After Generation

```
their-c-repo/
├── src/
│   ├── file1.c
│   └── file1.h
├── tests/
│   └── generated/
│       ├── test_file1.c    # AI-generated Unity tests
│       └── test_file2.c    # More generated tests
├── Makefile               # (if present)
└── README.md             # (if present)
```

## Support

### Getting Help
- Check the tool's README.md for detailed documentation
- Verify API key configuration
- Ensure Python 3.8+ is installed
- Test with the included examples first

### Example Repositories
Test the tool on these repositories:
- The included `examples/temperature_sensor/`
- Any open-source C project on GitHub
- Your own C codebases

---

**Ready to generate comprehensive Unity tests for any C repository!** 🚀
