#!/usr/bin/env python3
"""
Test the fix for content generation
"""
import subprocess
import os

def test_generation():
    print("Testing customer list generation...")
    
    # Run the generator
    result = subprocess.run(
        [sys.executable, "cstfind.py"],
        capture_output=True,
        text=True
    )
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    # Check for output files
    output_files = [f for f in os.listdir('output') if f.endswith('.md')]
    
    if output_files:
        latest = max(output_files, key=lambda x: os.path.getctime(os.path.join('output', x)))
        with open(os.path.join('output', latest), 'r') as f:
            content = f.read()
        
        print(f"\nGenerated file: {latest}")
        print(f"Content length: {len(content)} chars")
        print(f"Has table: {'|' in content}")
        
        if len(content) > 500 and '|' in content:
            print("✅ TEST PASSED: Content is substantial and has table structure")
            return True
        else:
            print("❌ TEST FAILED: Content insufficient")
            return False
    else:
        print("❌ TEST FAILED: No output file generated")
        return False

if __name__ == "__main__":
    import sys
    success = test_generation()
    sys.exit(0 if success else 1)