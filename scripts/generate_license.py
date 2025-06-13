import argparse
from src.activation import license_for

parser = argparse.ArgumentParser(description="Generate VigApp activation code")
parser.add_argument("code", help="Machine code shown on activation screen")
parser.add_argument("--counter", dest="counter", type=int, default=1,
                    help="License counter (default: 1)")
args = parser.parse_args()

print(license_for(args.code, args.counter))
