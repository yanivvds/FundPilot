"""
Quick connectivity test for MS SQL from the same environment as Vanna server.
This will help diagnose if the issue is VPN/network related.
"""

import os
import pyodbc
from dotenv import load_dotenv

def test_direct_connection():
    """Test direct pyodbc connection to troubleshoot network issues."""
    
    load_dotenv()
    
    conn_str = os.getenv("MSSQL_CONN_STR")
    print(f"🔍 Testing connection with: {conn_str}")
    
    try:
        print("🔌 Attempting direct pyodbc connection...")
        
        # Try with a shorter timeout first
        conn_str_with_timeout = conn_str + ";Connection Timeout=5;"
        
        conn = pyodbc.connect(conn_str_with_timeout)
        cursor = conn.cursor()
        
        print("✅ Connection successful!")
        
        # Try a simple query
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✅ Query successful! SQL Server version: {version[:50]}...")
        
        # Try listing tables
        cursor.execute("""
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_type='BASE TABLE'
            ORDER BY table_schema, table_name
        """)
        
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables in database")
        
        for i, (schema, table) in enumerate(tables[:5]):  # Show first 5
            print(f"  {i+1}. {schema}.{table}")
        
        if len(tables) > 5:
            print(f"  ... and {len(tables) - 5} more tables")
        
        cursor.close()
        conn.close()
        
        return True
        
    except pyodbc.OperationalError as e:
        if "Login timeout expired" in str(e):
            print("❌ Login timeout - Network/VPN connectivity issue")
            print("💡 The server can't reach your SQL Server over the network")
        elif "Login failed" in str(e):
            print("❌ Login failed - Credentials issue")
            print("💡 Connection reached server but authentication failed")
        else:
            print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing MS SQL connectivity from Vanna server context")
    print("=" * 60)
    
    success = test_direct_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Connection works! The issue might be elsewhere.")
    else:
        print("⚠️  Connection failed from this context.")
        print("\n💡 Solutions to try:")
        print("1. Make sure your VPN is connected")
        print("2. If using Docker/containers, check network settings")  
        print("3. Try running Vanna server directly on host (not in container)")
        print("4. Check if SQL Server allows connections from this IP")
        print("5. Verify firewall settings allow the connection")