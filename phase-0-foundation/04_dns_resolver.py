import socket

def resolve_domain(hostname):
    """
    Resolves a hostname to its IP address using the socket library.
    """
    print(f"\n🔍 Resolving: {hostname}")
    try:
        # socket.gethostbyname() is the most basic DNS resolution tool in Python
        ip_address = socket.gethostbyname(hostname)
        print(f"✅ IP Address: {ip_address}")
        return ip_address
    except socket.gaierror:
        # gaierror = Get Address Information Error
        print(f"❌ Error: Could not resolve {hostname}")
        return None

def resolve_domain_full(hostname):
    """
    Resolves a hostname and gets more detailed information.
    """
    print(f"\n🌐 Detailed Resolution for: {hostname}")
    try:
        # gethostbyname_ex returns (hostname, aliaslist, ipaddrlist)
        name, aliases, addresses = socket.gethostbyname_ex(hostname)
        print(f"   Canonical Name: {name}")
        print(f"   Aliases: {aliases}")
        print(f"   IP Addresses: {addresses}")
    except socket.gaierror as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test with some famous domains
    domains = ["google.com", "github.com", "python.org", "this-domain-should-fail.xyz"]
    
    for domain in domains:
        resolve_domain(domain)
        
    # Let's see some detailed info for a CDN-backed domain
    resolve_domain_full("www.google.com")
