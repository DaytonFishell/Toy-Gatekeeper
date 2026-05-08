#!/usr/bin/env python3
"""
Toy Gatekeeper - Educational Program Launcher

Launches protected Python wrappers with the required authorization token.

The token allows the protected wrapper to:
- Verify it was launched by an authorized gatekeeper
- Decrypt and run the embedded executable

This is for educational purposes only to demonstrate launcher-dependent execution.
"""

import sys
import os
import subprocess
import base64


def launch_protected_program(protected_py_path, args=None):
    """
    Launch a protected Python wrapper with authorization token.

    Args:
        protected_py_path: Path to the protected .py file
        args: Additional arguments to pass to the program
    """
    if args is None:
        args = []

    # Read the protected file to extract the encryption key
    # (in a real system, the gatekeeper would have its own key store)
    try:
        with open(protected_py_path, 'r') as f:
            content = f.read()

        # Extract encryption key from the wrapper
        # This is a simple extraction - production systems would be more secure
        import re
        key_match = re.search(r"ENCRYPTION_KEY = b'([^']*)'", content)
        if not key_match:
            print("ERROR: Could not extract encryption key from protected file.")
            print("The file may not be a valid protected wrapper.")
            sys.exit(1)

        encryption_key = key_match.group(1).encode('utf-8')

        # Generate the expected token
        token = "TOY_AUTHORIZED_" + base64.b64encode(encryption_key).decode()[:16]

    except Exception as e:
        print(f"ERROR: Failed to read protected file: {e}")
        sys.exit(1)

    # Set up environment with authorization token
    env = os.environ.copy()
    env['TOY_GATEKEEPER_TOKEN'] = token

    print(f"Launching protected program: {protected_py_path}")
    print("=" * 60)
    print()
    sys.stdout.flush()  # Ensure output is displayed before subprocess

    # Launch the protected program with the token
    try:
        cmd = [sys.executable, protected_py_path] + args
        result = subprocess.run(cmd, env=env)
        sys.exit(result.returncode)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR: Failed to launch protected program: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("Toy Gatekeeper - Educational Program Launcher")
        print()
        print("Usage:")
        print("  python gatekeeper.py <protected_file.py> [args...]")
        print()
        print("Or drag and drop a protected Python file onto gatekeeper.exe")
        print()
        print("This launches protected programs with the required authorization token.")
        sys.exit(1)

    protected_path = sys.argv[1]

    # Validate input file exists
    if not os.path.isfile(protected_path):
        print(f"ERROR: File not found: {protected_path}")
        sys.exit(1)

    # Check if it's a Python file
    if not protected_path.endswith('.py'):
        print(f"WARNING: File does not have .py extension: {protected_path}")
        print("Attempting to launch anyway...")
        print()

    # Get any additional arguments to pass through
    additional_args = sys.argv[2:] if len(sys.argv) > 2 else []

    # Launch the protected program
    launch_protected_program(protected_path, additional_args)


if __name__ == '__main__':
    main()
