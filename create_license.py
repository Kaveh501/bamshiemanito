from app import generate_licenses_file

if __name__ == "__main__":
    generate_licenses_file('license.data', 1000)
    print("License file created!")
