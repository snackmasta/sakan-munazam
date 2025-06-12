#!/usr/bin/env python3
"""
KEPServer Project Manager
Consolidated tool for managing KEPServer configurations
"""

import os
import subprocess
import sys

class KEPServerProjectManager:
    def __init__(self):
        self.scripts = {
            "create_channel_final.py": "Create new channels with guidance",
            "create_channel_simple.py": "Basic channel creation only", 
            "kepserver_template_generator.py": "Generate configuration templates",
            "check_api_capabilities.py": "Test API capabilities"
        }
        
        self.guides = {
            "KEPServer_Configuration_Guide.md": "Complete setup guide"
        }
    
    def show_banner(self):
        """Display welcome banner"""
        print("=" * 60)
        print("🏭 KEPServer Project Manager")
        print("=" * 60)
        print("Your one-stop tool for KEPServer configuration management")
        print()
    
    def check_files(self):
        """Check if all required files exist"""
        missing_files = []
        
        print("📋 Checking required files...")
        for script in self.scripts:
            if os.path.exists(script):
                print(f"✅ {script}")
            else:
                print(f"❌ {script}")
                missing_files.append(script)
        
        for guide in self.guides:
            if os.path.exists(guide):
                print(f"✅ {guide}")
            else:
                print(f"❌ {guide}")
                missing_files.append(guide)
        
        if missing_files:
            print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
            return False
        else:
            print("\n✅ All required files found!")
            return True
    
    def run_script(self, script_name):
        """Run a Python script"""
        try:
            print(f"\n🚀 Running {script_name}...")
            print("-" * 40)
            subprocess.run([sys.executable, script_name], check=True)
            print("-" * 40)
            print(f"✅ {script_name} completed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {script_name}: {e}")
        except FileNotFoundError:
            print(f"❌ Script not found: {script_name}")
    
    def open_guide(self, guide_name):
        """Open a guide file"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(guide_name)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open', guide_name])
            print(f"📖 Opened {guide_name}")
        except Exception as e:
            print(f"❌ Could not open {guide_name}: {e}")
            print(f"📝 Please manually open: {os.path.abspath(guide_name)}")
    
    def show_quick_start(self):
        """Show quick start guide"""
        print("\n🚀 Quick Start Guide")
        print("=" * 30)
        print("1. **Test Connection**: Run API capability check")
        print("2. **Create Channel**: Use the channel creation tool")
        print("3. **Follow Guide**: Manual device/tag configuration")
        print("4. **Use Templates**: Generate standardized configs")
        print()
        print("💡 Tip: Start with option 1 to test your KEPServer connection!")
        print()
    
    def show_main_menu(self):
        """Display main menu"""
        print("\n📋 Main Menu")
        print("=" * 20)
        print("🔧 Scripts:")
        for i, (script, description) in enumerate(self.scripts.items(), 1):
            print(f"  {i}. {description}")
        
        print("\n📚 Documentation:")
        start_idx = len(self.scripts) + 1
        for i, (guide, description) in enumerate(self.guides.items(), start_idx):
            print(f"  {i}. {description}")
        
        print(f"\n  {start_idx + len(self.guides)}. Show Quick Start")
        print(f"  {start_idx + len(self.guides) + 1}. Exit")
        print()
    
    def run(self):
        """Main program loop"""
        self.show_banner()
        
        if not self.check_files():
            print("\n❌ Cannot proceed with missing files.")
            return
        
        self.show_quick_start()
        
        while True:
            self.show_main_menu()
            choice = input("👉 Select option: ").strip()
            
            try:
                choice_num = int(choice)
                
                # Scripts
                if 1 <= choice_num <= len(self.scripts):
                    script_name = list(self.scripts.keys())[choice_num - 1]
                    self.run_script(script_name)
                
                # Documentation
                elif choice_num == len(self.scripts) + 1:
                    guide_name = list(self.guides.keys())[0]
                    self.open_guide(guide_name)
                
                # Quick Start
                elif choice_num == len(self.scripts) + len(self.guides) + 1:
                    self.show_quick_start()
                
                # Exit
                elif choice_num == len(self.scripts) + len(self.guides) + 2:
                    print("\n👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            
            # Wait for user to read output
            input("\n⏸️  Press Enter to continue...")

def main():
    manager = KEPServerProjectManager()
    manager.run()

if __name__ == "__main__":
    main()
