import argparse
import os
import sys

# Ensure the "src" package can be imported when running this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.activation import license_for

parser = argparse.ArgumentParser(description="Generate VigApp activation code")
parser.add_argument("code", help="Machine code shown on activation screen")
parser.add_argument("--counter", dest="counter", type=int, default=1,
                    help="License counter (default: 1)")
args = parser.parse_args()

print(license_for(args.code, args.counter))
