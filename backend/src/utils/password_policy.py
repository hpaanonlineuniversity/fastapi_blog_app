# utils/password_policy.py
import re
from typing import Dict, List

class PasswordPolicy:
    @staticmethod
    def validate_password(password: str) -> Dict[str, bool]:
        """
        Validate password against policy
        Returns: Dict with validation results and error messages
        """
        if not password:
            return {
                "is_valid": False,
                "errors": ["Password is required"],
                "score": 0
            }
        
        errors = []
        score = 0
        
        # Length check (8+ characters)
        if len(password) >= 8:
            score += 1
        else:
            errors.append("At least 8 characters")
        
        # Uppercase check
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            errors.append("One uppercase letter")
        
        # Lowercase check
        if re.search(r'[a-z]', password):
            score += 1
        else:
            errors.append("One lowercase letter")
        
        # Number check
        if re.search(r'\d', password):
            score += 1
        else:
            errors.append("One number")
        
        # Special character check
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            errors.append("One special character")
        
        # Strength rating
        strength = "weak"
        if score >= 4:
            strength = "medium"
        if score == 5:
            strength = "strong"
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "score": score,
            "strength": strength
        }
    
    @staticmethod
    def generate_strong_password() -> str:
        """Generate a strong password that meets policy"""
        import random
        import string
        
        # Define character sets
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        special_chars = '!@#$%^&*()'
        
        # Ensure at least one of each type
        password = [
            random.choice(uppercase),
            random.choice(lowercase),
            random.choice(digits),
            random.choice(special_chars)
        ]
        
        # Fill remaining length with random characters
        remaining_length = random.randint(4, 8)  # Total 8-12 characters
        all_chars = uppercase + lowercase + digits + special_chars
        password.extend(random.choice(all_chars) for _ in range(remaining_length))
        
        # Shuffle the password
        random.shuffle(password)
        
        return ''.join(password)