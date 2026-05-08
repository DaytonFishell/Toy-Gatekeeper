# Toy Protector + Gatekeeper Demo

This is a simple educational demonstration of copy-protection-style launcher-dependent execution. It shows how a protected program can refuse to run unless launched through an authorized gatekeeper.

**This is not real DRM.** It is intentionally simple, transparent, and meant for learning how launcher-dependent execution works.

## Overview

The workflow:

```
hello.exe
  ↓ drag onto protector.py (or run: python protector.py hello.exe)
protected_hello.py
  ↓ drag onto gatekeeper.py (or run: python gatekeeper.py protected_hello.py)
original program runs
```

The protected file is a small wrapper script that contains an encrypted copy of the original executable. It refuses to run unless launched through the gatekeeper.

## What You Get

Three components:

1. **hello.exe** — A basic "Hello World" program to protect (compiled from hello.c)
2. **protector.py** — Takes an executable and creates a protected Python wrapper
3. **gatekeeper.py** — Launches protected files with a temporary authorization token

## How It Works

The protected wrapper checks for a token in an environment variable:

```
TOY_GATEKEEPER_TOKEN
```

- If the token matches: it decrypts the embedded original program, writes it to a temporary folder, runs it, then deletes it
- If the token is missing or wrong: it refuses to run

## Installation

### Requirements

- Python 3.11 or newer
- C compiler (gcc or similar) to build hello.exe
- Python packages:

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install cryptography
pip install pyinstaller  # Optional: for creating .exe files
```

## Quick Start

### Step 1: Build the Hello World Program

Compile the example program:

```bash
gcc hello.c -o hello.exe
```

Test it works:

```bash
./hello.exe
```

You should see: `Hello, World! This is a protected program.`

### Step 2: Protect the Executable

Run the protector:

```bash
python protector.py hello.exe
```

This creates `protected_hello.py` containing an encrypted copy of hello.exe.

### Step 3: Try Running the Protected File Directly

```bash
python protected_hello.py
```

You'll see:
```
ERROR: This protected program requires a gatekeeper token.
Please launch through gatekeeper.py
```

### Step 4: Launch Through the Gatekeeper

```bash
python gatekeeper.py protected_hello.py
```

Now it works! You should see:
```
Launching protected program: protected_hello.py
============================================================

Hello, World! This is a protected program.
```

## Making Standalone Executables

You can use PyInstaller to create standalone .exe files:

```bash
# Create protector.exe
pyinstaller --onefile protector.py

# Create gatekeeper.exe
pyinstaller --onefile gatekeeper.py
```

Then you can drag and drop files:
- Drag `hello.exe` onto `protector.exe` to create `protected_hello.py`
- Drag `protected_hello.py` onto `gatekeeper.exe` to run it

## How to Protect Other Programs

The protector works with any executable:

```bash
python protector.py /path/to/your/program.exe
```

This creates `protected_program.py` which can only be launched via the gatekeeper.

## Technical Details

### Encryption

- Uses the `cryptography` library with Fernet (symmetric encryption)
- Each protected file gets a unique random encryption key
- The key is embedded in the protected wrapper
- The gatekeeper extracts the key and generates the matching token

### Token Generation

The token is generated as:
```python
token = "TOY_AUTHORIZED_" + base64.b64encode(encryption_key)[:16]
```

This is intentionally simple. In a real system, you would use:
- Asymmetric cryptography (public/private keys)
- Hardware tokens or secure enclaves
- Time-limited tokens
- Network-based authorization servers

### Process Flow

1. **Protector** (`protector.py`):
   - Reads the original executable
   - Generates a random encryption key
   - Encrypts the executable with Fernet
   - Embeds the encrypted data in a Python wrapper
   - The wrapper includes decryption and token-checking logic

2. **Protected Wrapper** (`protected_*.py`):
   - Checks for `TOY_GATEKEEPER_TOKEN` environment variable
   - Verifies the token matches the expected value
   - Decrypts the embedded executable
   - Writes it to a temporary file
   - Executes the temporary file
   - Cleans up the temporary file

3. **Gatekeeper** (`gatekeeper.py`):
   - Reads the protected wrapper to extract the encryption key
   - Generates the matching authorization token
   - Sets the `TOY_GATEKEEPER_TOKEN` environment variable
   - Launches the protected wrapper

## Limitations & Educational Purpose

This is a **toy demonstration** to teach concepts. It is NOT secure for production use because:

- ❌ The encryption key is embedded in the protected file (readable by anyone)
- ❌ The token generation algorithm is simple and predictable
- ❌ No code obfuscation (the Python wrapper is easily readable)
- ❌ No anti-debugging or tamper detection
- ❌ No hardware or network-based authorization
- ❌ The original executable is written to disk unencrypted (briefly)

Real copy protection systems use:
- Hardware dongles or TPM chips
- Online activation servers
- Code obfuscation and anti-tampering
- Kernel-level protection
- Secure boot chains

## Use Cases for Learning

This demo teaches:
- How launcher-dependent execution works
- Environment variable-based authorization
- Symmetric encryption basics
- Temporary file handling
- Parent-child process communication

## License

This is educational code provided for learning purposes. Use responsibly and ethically.

## Security Notice

**Do not use this for protecting sensitive or valuable software.** This is a teaching tool that demonstrates concepts but is not cryptographically secure against determined attackers.

If you're working on real software protection, consult with security professionals and use established commercial solutions.
