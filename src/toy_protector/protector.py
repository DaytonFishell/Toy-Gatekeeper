#!/usr/bin/env python3
"""
Toy Protector - Educational Copy Protection Tool

Takes an executable file and creates a protected Python wrapper that:
- Contains an encrypted copy of the original executable
- Requires a valid token from the gatekeeper to run
- Decrypts, executes, and cleans up the original program

This is for educational purposes only to demonstrate launcher-dependent execution.
"""

import sys
import os
import base64


def _load_fernet():
    """Load Fernet at runtime to avoid hard import dependency at module load."""
    try:
        from importlib import import_module
        return import_module("cryptography.fernet").Fernet
    except Exception:
        return None


def create_protected_wrapper(input_exe_path, output_py_path, encryption_key):
    """
    Create a protected Python wrapper containing an encrypted executable.

    Args:
        input_exe_path: Path to the original executable to protect
        output_py_path: Path where the protected Python file will be created
        encryption_key: Fernet encryption key (bytes)
    """
    # Read the original executable
    with open(input_exe_path, 'rb') as f:
        original_data = f.read()

    # Encrypt the executable
    Fernet = _load_fernet()
    if Fernet is None:
        raise RuntimeError("cryptography package not installed. Install with: pip install cryptography")
    fernet = Fernet(encryption_key)
    encrypted_data = fernet.encrypt(original_data)

    # Encode to base64 for embedding in Python script
    encrypted_b64 = base64.b64encode(encrypted_data).decode('ascii')

    # Get original filename
    original_name = os.path.basename(input_exe_path)

    # Create the protected wrapper script
    wrapper_code = f'''#!/usr/bin/env python3
"""
Protected executable wrapper - created by Toy Protector
Original file: {original_name}

This wrapper requires a valid TOY_GATEKEEPER_TOKEN to run.
Launch through gatekeeper.py to execute the protected program.
"""

import os
import sys
import base64
import tempfile
import subprocess
from pathlib import Path

# The encryption key (in a real system, this would be more secure)
ENCRYPTION_KEY = {repr(encryption_key)}

# Encrypted payload (base64 encoded)
ENCRYPTED_PAYLOAD = """
{encrypted_b64}
"""

def main():
    # Check for gatekeeper token
    token = os.environ.get('TOY_GATEKEEPER_TOKEN')

    if not token:
        print("ERROR: This protected program requires a gatekeeper token.")
        print("Please launch through gatekeeper.py")
        sys.exit(1)

    # Verify token (simple check - in real systems this would be more robust)
    expected_token = "TOY_AUTHORIZED_" + base64.b64encode(ENCRYPTION_KEY).decode()[:16]

    if token != expected_token:
        print("ERROR: Invalid gatekeeper token.")
        print("Please launch through the correct gatekeeper.")
        sys.exit(1)

    print("Token verified. Decrypting and launching protected program...")
    print()

    try:
        # Import cryptography inside to handle missing dependency gracefully
        from cryptography.fernet import Fernet

        # Decode and decrypt the payload
        encrypted_data = base64.b64decode(ENCRYPTED_PAYLOAD.strip())
        fernet = Fernet(ENCRYPTION_KEY)
        decrypted_data = fernet.decrypt(encrypted_data)

        # Create a temporary file for the executable
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.exe', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(decrypted_data)

        # Make it executable (Unix/Linux)
        try:
            os.chmod(tmp_path, 0o755)
        except:
            pass  # Windows doesn't need chmod

        # Run the decrypted executable
        result = subprocess.run([tmp_path] + sys.argv[1:])

        # Clean up
        try:
            os.unlink(tmp_path)
        except:
            pass  # Best effort cleanup

        sys.exit(result.returncode)

    except ImportError:
        print("ERROR: cryptography package not installed.")
        print("Install with: pip install cryptography")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to decrypt or run protected program: {{e}}")
        sys.exit(1)

if __name__ == '__main__':
    main()
'''

    # Write the protected wrapper
    with open(output_py_path, 'w') as f:
        f.write(wrapper_code)

    # Make it executable
    try:
        os.chmod(output_py_path, 0o755)
    except:
        pass  # Windows doesn't use chmod


def main():
    if len(sys.argv) != 2:
        print("Toy Protector - Educational Copy Protection Tool")
        print()
        print("Usage:")
        print("  python protector.py <executable_file>")
        print()
        print("Or drag and drop an executable onto protector.exe")
        print()
        print("This will create a protected Python wrapper file that requires")
        print("the gatekeeper to run.")
        sys.exit(1)

    input_path = sys.argv[1]

    # Validate input file exists
    if not os.path.isfile(input_path):
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    # Generate output filename
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = f"protected_{base_name}.py"

    # Generate a random encryption key
    Fernet = _load_fernet()
    if Fernet is None:
        print("ERROR: cryptography package not installed.")
        print("Install with: pip install cryptography")
        sys.exit(1)
    encryption_key = Fernet.generate_key()

    print(f"Protecting: {input_path}")
    print(f"Output: {output_path}")
    print(f"Encryption key: {encryption_key.decode()}")
    print()

    # Create the protected wrapper
    create_protected_wrapper(input_path, output_path, encryption_key)

    print(f"SUCCESS: Protected file created: {output_path}")
    print()
    print("To run the protected program:")
    print(f"  python gatekeeper.py {output_path}")
    print()
    print("Or drag and drop the protected file onto gatekeeper.exe")


if __name__ == '__main__':
    main()
