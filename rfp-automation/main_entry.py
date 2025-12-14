
if __name__ == "__main__":
    # Simple CLI test:
    # python main.py path/to/rfp.txt
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <rfp_file_path>")
    else:
        process_rfp(sys.argv[1])
