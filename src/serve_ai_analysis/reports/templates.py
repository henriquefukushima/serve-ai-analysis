"""Report templates module for tennis serve analysis."""

from rich.console import Console

console = Console()

class ReportTemplate:
    """Template for PDF reports."""
    
    def __init__(self):
        pass
    
    def get_template(self):
        """Get report template."""
        console.print("[blue]Loading report template...[/blue]")
        # TODO: Implement template loading
        console.print("✅ Template loaded")
        return ""
