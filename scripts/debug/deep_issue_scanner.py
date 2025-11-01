#!/usr/bin/env python3
"""
Deep Issue Scanner for Student Tracking System
Detects and reports potential issues across the entire codebase
"""
import os
import sys
import re
import ast
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {str(e)}")
    sys.exit(1)

class IssueScanner:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.base_dir = settings.BASE_DIR

    def log_issue(self, severity, category, file_path, line_num, description, suggestion=""):
        self.issues.append({
            'severity': severity,
            'category': category,
            'file': file_path,
            'line': line_num,
            'description': description,
            'suggestion': suggestion
        })

    def log_warning(self, category, file_path, description):
        self.warnings.append({
            'category': category,
            'file': file_path,
            'description': description
        })

    def scan_python_files(self):
        """Scan Python files for common issues."""
        print("🔍 Scanning Python files...")
        
        python_files = []
        for root, dirs, files in os.walk(self.base_dir):
            # Skip virtual environment and migrations
            if 'venv' in root or '__pycache__' in root or 'migrations' in root:
                continue
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for file_path in python_files:
            self._scan_python_file(file_path)
        
        print(f"  📁 Scanned {len(python_files)} Python files")

    def _scan_python_file(self, file_path):
        """Scan individual Python file for issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Parse AST for syntax errors
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.log_issue('CRITICAL', 'Syntax', file_path, e.lineno, 
                              f"Syntax error: {e.msg}", "Fix syntax error")
            
            # Check for common issues
            for i, line in enumerate(lines, 1):
                self._check_line_issues(file_path, i, line)
                
        except Exception as e:
            self.log_warning('File Access', file_path, f"Could not read file: {str(e)}")

    def _check_line_issues(self, file_path, line_num, line):
        """Check individual line for issues."""
        
        # Check for missing imports
        if 'from django.db import models' in line and 'models.py' in file_path:
            # Good practice
            pass
        
        # Check for hardcoded secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                self.log_issue('HIGH', 'Security', file_path, line_num,
                              "Potential hardcoded secret", "Move to environment variables")
        
        # Check for TODO/FIXME comments
        if re.search(r'#\s*(TODO|FIXME|HACK)', line, re.IGNORECASE):
            self.log_warning('Code Quality', file_path, f"Line {line_num}: Unresolved TODO/FIXME")
        
        # Check for print statements (should use logging)
        if re.search(r'\bprint\s*\(', line) and 'test' not in file_path.lower():
            self.log_warning('Code Quality', file_path, f"Line {line_num}: Use logging instead of print")
        
        # Check for bare except clauses
        if re.search(r'except\s*:', line):
            self.log_issue('MEDIUM', 'Error Handling', file_path, line_num,
                          "Bare except clause", "Specify exception type")

    def scan_templates(self):
        """Scan HTML templates for issues."""
        print("🔍 Scanning templates...")
        
        template_dir = os.path.join(self.base_dir, 'templates')
        if not os.path.exists(template_dir):
            self.log_issue('HIGH', 'Configuration', 'templates/', 0,
                          "Templates directory not found", "Create templates directory")
            return
        
        template_files = []
        for root, dirs, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    template_files.append(os.path.join(root, file))
        
        for file_path in template_files:
            self._scan_template_file(file_path)
        
        print(f"  📁 Scanned {len(template_files)} template files")

    def _scan_template_file(self, file_path):
        """Scan individual template file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for unescaped output
                if re.search(r'\{\{\s*[^|]*\s*\|safe\s*\}\}', line):
                    self.log_issue('MEDIUM', 'Security', file_path, i,
                                  "Potentially unsafe template output", "Verify safe filter usage")
                
                # Check for missing CSRF token in forms
                if '<form' in line and 'method="post"' in line.lower():
                    # Look for csrf_token in nearby lines
                    csrf_found = any('csrf_token' in lines[j] 
                                   for j in range(max(0, i-2), min(len(lines), i+10)))
                    if not csrf_found:
                        self.log_issue('HIGH', 'Security', file_path, i,
                                      "POST form without CSRF token", "Add {% csrf_token %}")
                
                # Check for hardcoded URLs
                if re.search(r'href\s*=\s*["\'][^"\']*(/[^"\']+)["\']', line):
                    if not re.search(r'\{\%\s*url\s+', line):
                        self.log_warning('Code Quality', file_path, 
                                       f"Line {i}: Consider using {{% url %}} tag")
                        
        except Exception as e:
            self.log_warning('File Access', file_path, f"Could not read template: {str(e)}")

    def scan_static_files(self):
        """Scan static files for issues."""
        print("🔍 Scanning static files...")
        
        static_dir = os.path.join(self.base_dir, 'static')
        if not os.path.exists(static_dir):
            self.log_warning('Configuration', 'static/', "Static directory not found")
            return
        
        js_files = []
        css_files = []
        
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file.endswith('.js'):
                    js_files.append(os.path.join(root, file))
                elif file.endswith('.css'):
                    css_files.append(os.path.join(root, file))
        
        # Scan JavaScript files
        for file_path in js_files:
            self._scan_js_file(file_path)
        
        print(f"  📁 Scanned {len(js_files)} JavaScript files, {len(css_files)} CSS files")

    def _scan_js_file(self, file_path):
        """Scan JavaScript file for issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for console.log (should be removed in production)
                if re.search(r'console\.(log|debug|info)', line):
                    self.log_warning('Code Quality', file_path, 
                                   f"Line {i}: Remove console statements for production")
                
                # Check for eval usage (security risk)
                if re.search(r'\beval\s*\(', line):
                    self.log_issue('HIGH', 'Security', file_path, i,
                                  "eval() usage detected", "Avoid eval() for security")
                
                # Check for innerHTML usage (potential XSS)
                if re.search(r'\.innerHTML\s*=', line):
                    self.log_issue('MEDIUM', 'Security', file_path, i,
                                  "innerHTML usage", "Consider using textContent or sanitize input")
                        
        except Exception as e:
            self.log_warning('File Access', file_path, f"Could not read JS file: {str(e)}")

    def scan_django_configuration(self):
        """Scan Django configuration for issues."""
        print("🔍 Scanning Django configuration...")
        
        # Check settings.py
        settings_file = os.path.join(self.base_dir, 'enhanced_timetable_system', 'settings.py')
        if os.path.exists(settings_file):
            self._scan_settings_file(settings_file)
        
        # Check URLs
        self._scan_url_configurations()
        
        # Check models
        self._scan_model_configurations()

    def _scan_settings_file(self, file_path):
        """Scan settings.py for configuration issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for DEBUG in production
            if 'DEBUG = True' in content:
                self.log_warning('Configuration', file_path, 
                               "DEBUG=True should be False in production")
            
            # Check for ALLOWED_HOSTS
            if 'ALLOWED_HOSTS = []' in content:
                self.log_issue('MEDIUM', 'Configuration', file_path, 0,
                              "Empty ALLOWED_HOSTS", "Configure allowed hosts for production")
            
            # Check for SECRET_KEY
            if re.search(r"SECRET_KEY\s*=\s*['\"][^'\"]{20,}['\"]", content):
                if 'django-insecure' in content:
                    self.log_issue('HIGH', 'Security', file_path, 0,
                                  "Using default/insecure SECRET_KEY", 
                                  "Generate new SECRET_KEY for production")
            
        except Exception as e:
            self.log_warning('File Access', file_path, f"Could not read settings: {str(e)}")

    def _scan_url_configurations(self):
        """Check URL configurations for issues."""
        try:
            from django.urls import reverse
            from django.urls.exceptions import NoReverseMatch
            
            critical_urls = [
                'accounts:landing',
                'accounts:login',
                'accounts:student_dashboard',
                'accounts:admin_dashboard',
                'accounts:teacher_dashboard'
            ]
            
            for url_name in critical_urls:
                try:
                    reverse(url_name)
                except NoReverseMatch:
                    self.log_issue('HIGH', 'URL Configuration', 'urls.py', 0,
                                  f"URL {url_name} cannot be reversed", 
                                  f"Check URL pattern for {url_name}")
                    
        except Exception as e:
            self.log_warning('URL Configuration', 'urls.py', f"Could not check URLs: {str(e)}")

    def _scan_model_configurations(self):
        """Check model configurations."""
        try:
            from accounts.models import User, StudentProfile, AdminProfile, TeacherProfile
            from timetable.models import Course, Subject, Teacher, TimetableEntry
            from ai_features.models import AIChat, StudyRecommendation
            
            # Check for missing __str__ methods
            models_to_check = [
                ('accounts.models', 'StudentProfile', StudentProfile),
                ('timetable.models', 'Course', Course),
                ('timetable.models', 'Subject', Subject),
                ('ai_features.models', 'AIChat', AIChat),
            ]
            
            for module_name, model_name, model_class in models_to_check:
                if not hasattr(model_class, '__str__'):
                    self.log_warning('Code Quality', f'{module_name}.py',
                                   f"{model_name} missing __str__ method")
                    
        except Exception as e:
            self.log_warning('Models', 'models.py', f"Could not check models: {str(e)}")

    def scan_security_issues(self):
        """Scan for security-related issues."""
        print("🔍 Scanning for security issues...")
        
        # Check for SQL injection vulnerabilities
        self._check_sql_injection_patterns()
        
        # Check for XSS vulnerabilities
        self._check_xss_patterns()
        
        # Check authentication/authorization
        self._check_auth_patterns()

    def _check_sql_injection_patterns(self):
        """Check for potential SQL injection issues."""
        # Scan view files for raw SQL
        view_files = [
            'accounts/views.py',
            'accounts/student_views.py', 
            'accounts/admin_views.py',
            'accounts/teacher_views.py'
        ]
        
        for file_path in view_files:
            full_path = os.path.join(self.base_dir, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for raw SQL
                    if re.search(r'\.raw\s*\(', content):
                        self.log_issue('MEDIUM', 'Security', file_path, 0,
                                      "Raw SQL usage detected", "Use Django ORM or parameterized queries")
                    
                    # Check for string formatting in queries
                    if re.search(r'\.filter\([^)]*%', content):
                        self.log_issue('MEDIUM', 'Security', file_path, 0,
                                      "Potential SQL injection in filter", "Use Django ORM properly")
                        
                except Exception:
                    pass

    def _check_xss_patterns(self):
        """Check for XSS vulnerabilities."""
        template_dir = os.path.join(self.base_dir, 'templates')
        if os.path.exists(template_dir):
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Check for |safe usage
                            if '|safe' in content:
                                self.log_warning('Security', file_path.replace(str(self.base_dir), ''),
                                               "Using |safe filter - ensure content is sanitized")
                        except Exception:
                            pass

    def _check_auth_patterns(self):
        """Check authentication/authorization patterns."""
        view_files = [
            'accounts/student_views.py',
            'accounts/admin_views.py', 
            'accounts/teacher_views.py'
        ]
        
        for file_path in view_files:
            full_path = os.path.join(self.base_dir, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Check for missing @login_required
                    functions = re.findall(r'def\s+(\w+)\s*\([^)]*request', content)
                    for func_name in functions:
                        if func_name.startswith('_'):  # Skip private functions
                            continue
                        
                        # Look for @login_required before function
                        func_pattern = f'def\s+{func_name}'
                        match = re.search(func_pattern, content)
                        if match:
                            before_func = content[:match.start()]
                            if '@login_required' not in before_func[-200:]:
                                self.log_warning('Security', file_path,
                                               f"Function {func_name} might need @login_required")
                        
                except Exception:
                    pass

    def generate_report(self):
        """Generate comprehensive issue report."""
        print("\n" + "="*80)
        print("🔍 DEEP ISSUE SCAN RESULTS")
        print("="*80)
        
        # Group issues by severity
        critical_issues = [i for i in self.issues if i['severity'] == 'CRITICAL']
        high_issues = [i for i in self.issues if i['severity'] == 'HIGH']
        medium_issues = [i for i in self.issues if i['severity'] == 'MEDIUM']
        low_issues = [i for i in self.issues if i['severity'] == 'LOW']
        
        total_issues = len(self.issues)
        total_warnings = len(self.warnings)
        
        print(f"\n📊 SUMMARY:")
        print(f"  🔥 Critical Issues: {len(critical_issues)}")
        print(f"  🚨 High Priority:   {len(high_issues)}")
        print(f"  ⚠️  Medium Priority: {len(medium_issues)}")
        print(f"  ℹ️  Low Priority:    {len(low_issues)}")
        print(f"  💡 Warnings:        {total_warnings}")
        print(f"  📈 Total:           {total_issues + total_warnings}")
        
        # Show critical and high issues first
        if critical_issues:
            print(f"\n🔥 CRITICAL ISSUES ({len(critical_issues)}):")
            for issue in critical_issues:
                print(f"  📁 {issue['file']}:{issue['line']}")
                print(f"     {issue['description']}")
                if issue['suggestion']:
                    print(f"     💡 {issue['suggestion']}")
                print()
        
        if high_issues:
            print(f"\n🚨 HIGH PRIORITY ISSUES ({len(high_issues)}):")
            for issue in high_issues:
                print(f"  📁 {issue['file']}:{issue['line']}")
                print(f"     {issue['description']}")
                if issue['suggestion']:
                    print(f"     💡 {issue['suggestion']}")
                print()
        
        # Show medium issues
        if medium_issues:
            print(f"\n⚠️ MEDIUM PRIORITY ISSUES ({len(medium_issues)}):")
            for issue in medium_issues[:5]:  # Show first 5
                print(f"  📁 {issue['file']}:{issue['line']}")
                print(f"     {issue['description']}")
                if issue['suggestion']:
                    print(f"     💡 {issue['suggestion']}")
                print()
            
            if len(medium_issues) > 5:
                print(f"  ... and {len(medium_issues) - 5} more medium issues")
        
        # Show some warnings
        if self.warnings:
            print(f"\n💡 WARNINGS (showing first 10 of {len(self.warnings)}):")
            for warning in self.warnings[:10]:
                print(f"  📁 {warning['file']}")
                print(f"     {warning['description']}")
                print()
        
        # Overall health score
        total_score = 100
        total_score -= len(critical_issues) * 20
        total_score -= len(high_issues) * 10
        total_score -= len(medium_issues) * 5
        total_score -= len(low_issues) * 2
        total_score = max(0, total_score)
        
        print(f"\n🎯 SYSTEM HEALTH SCORE: {total_score}/100")
        
        if total_score >= 90:
            print("🎉 Excellent! Your system is in great shape.")
        elif total_score >= 70:
            print("✅ Good! A few minor issues to address.")
        elif total_score >= 50:
            print("⚠️ Moderate. Some important issues need attention.")
        else:
            print("🚨 Poor. Critical issues need immediate attention.")
        
        return total_issues, total_warnings

def main():
    """Run deep issue scan."""
    scanner = IssueScanner()
    
    print("🚀 Student Tracking System - Deep Issue Scanner")
    print("="*60)
    
    # Run all scans
    scanner.scan_python_files()
    scanner.scan_templates()
    scanner.scan_static_files()
    scanner.scan_django_configuration()
    scanner.scan_security_issues()
    
    # Generate report
    issues, warnings = scanner.generate_report()
    
    return 0 if issues == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
