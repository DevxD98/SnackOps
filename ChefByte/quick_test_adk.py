"""
Quick Test - Single query to verify ADK agent works
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from adk_agent import ChefByteADKAgent

def main():
    print("="*60)
    print("ChefByte ADK Agent - Quick Test")
    print("="*60)
    
    # Create agent
    print("\n1. Initializing agent...")
    try:
        agent = ChefByteADKAgent()
        print("   ✓ Agent initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test simple query
    print("\n2. Testing simple query...")
    query = "Hi! I have tomatoes, onions, and rice. What can I cook?"
    print(f"   Query: {query}")
    
    try:
        result = agent.run(query)
        
        if result['success']:
            print(f"\n   ✓ Success!")
            print(f"\n   Response:")
            print(f"   {'-'*56}")
            print(f"   {result['response']}")
            print(f"   {'-'*56}")
        else:
            print(f"\n   ✗ Failed: {result.get('error')}")
    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("Test complete!")
    print("="*60)

if __name__ == "__main__":
    main()
