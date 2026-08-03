#!/usr/bin/env python3
"""
Download Real Dataset Samples for Testing

This script downloads authentic samples from real datasets used in LLM fine-tuning.
All datasets are from official sources with proper licenses.

Run this script to populate tests/fixtures/datasets/ with real data.
"""

import json
import os
from pathlib import Path
from typing import List, Dict

# Try to import datasets library, fall back to manual download
try:
    from datasets import load_dataset
    HAS_DATASETS_LIB = True
except ImportError:
    HAS_DATASETS_LIB = False
    print("Warning: 'datasets' library not installed. Install with: pip install datasets")

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests")
    exit(1)


class RealDatasetDownloader:
    """Downloads real dataset samples from official sources."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def download_alpaca_sample(self, num_samples: int = 12) -> List[Dict]:
        """
        Download real Alpaca dataset samples.
        
        Source: https://github.com/tatsu-lab/stanford_alpaca
        License: CC BY-NC-SA 4.0
        """
        print(f"Downloading {num_samples} samples from Stanford Alpaca...")
        
        # Direct download from GitHub (official source)
        url = "https://raw.githubusercontent.com/tatsu-lab/stanford_alpaca/main/alpaca_data.json"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Take first num_samples
            samples = data[:num_samples]
            
            # Convert to our format (instruction/input/output -> instruction/response)
            formatted = []
            for item in samples:
                formatted.append({
                    "instruction": item.get("instruction", ""),
                    "response": item.get("output", "")
                })
            
            return formatted
            
        except Exception as e:
            print(f"Failed to download Alpaca: {e}")
            return self._get_fallback_alpaca(num_samples)
    
    def _get_fallback_alpaca(self, num_samples: int) -> List[Dict]:
        """Fallback Alpaca samples if download fails."""
        return [
            {
                "instruction": "Give three tips for staying healthy.",
                "response": "1. Maintain a balanced diet rich in fruits, vegetables, and whole grains while limiting processed foods and sugars. 2. Exercise regularly, aiming for at least 150 minutes of moderate aerobic activity per week. 3. Get sufficient sleep (7-9 hours nightly) and manage stress through mindfulness or relaxation techniques."
            },
            {
                "instruction": "What is the capital of France?",
                "response": "The capital of France is Paris. It's the largest city in France and serves as the country's political, economic, and cultural center."
            },
            {
                "instruction": "Explain the concept of machine learning to a 10-year-old.",
                "response": "Machine learning is like teaching a computer to learn from examples, similar to how you learn. Instead of programming every rule, you show the computer thousands of examples, and it figures out patterns on its own. For instance, if you want to teach it to recognize cats, you show it many cat photos, and eventually it learns what makes a cat a cat."
            },
            {
                "instruction": "Write a Python function to calculate factorial.",
                "response": "Here's a Python function to calculate factorial using recursion:\n\ndef factorial(n):\n    if n == 0 or n == 1:\n        return 1\n    else:\n        return n * factorial(n-1)\n\nAlternatively, using iteration:\ndef factorial_iterative(n):\n    result = 1\n    for i in range(2, n+1):\n        result *= i\n    return result"
            }
        ][:num_samples]
    
    def download_dolly_sample(self, num_samples: int = 12) -> List[Dict]:
        """
        Download real Databricks Dolly dataset samples.
        
        Source: https://huggingface.co/datasets/databricks/databricks-dolly-15k
        License: CC BY-SA 3.0
        """
        print(f"Downloading {num_samples} samples from Databricks Dolly...")
        
        if HAS_DATASETS_LIB:
            try:
                dataset = load_dataset("databricks/databricks-dolly-15k", split="train", streaming=True)
                samples = []
                for i, item in enumerate(dataset):
                    if i >= num_samples:
                        break
                    samples.append({
                        "instruction": item.get("instruction", ""),
                        "response": item.get("response", "")
                    })
                return samples
            except Exception as e:
                print(f"Failed to load Dolly via datasets library: {e}")
        
        # Fallback to known Dolly-style examples
        return self._get_fallback_dolly(num_samples)
    
    def _get_fallback_dolly(self, num_samples: int) -> List[Dict]:
        """Fallback Dolly samples."""
        return [
            {
                "instruction": "Explain the water cycle in simple terms.",
                "response": "The water cycle is how water moves around our planet. The sun heats up water in oceans and lakes, turning it into water vapor (gas) that rises into the air. As it goes higher, it cools down and forms clouds. When the clouds get heavy, water falls back to Earth as rain or snow. This water eventually flows back into oceans and lakes, and the cycle starts again."
            },
            {
                "instruction": "What are the main differences between Python and JavaScript?",
                "response": "Python is primarily used for backend development, data science, and scripting. It's known for readability and simplicity. JavaScript is primarily used for web development (both frontend and backend with Node.js). Key differences: Python uses indentation for blocks, JavaScript uses braces; Python is generally slower but has better data science libraries; JavaScript runs in browsers natively."
            }
        ][:num_samples]
    
    def create_high_quality_dataset(self) -> List[Dict]:
        """Create high_quality.jsonl from real Alpaca + Dolly samples."""
        print("\n=== Creating high_quality dataset ===")
        
        # Mix of real Alpaca and Dolly samples
        alpaca_samples = self.download_alpaca_sample(8)
        dolly_samples = self.download_dolly_sample(4)
        
        combined = alpaca_samples + dolly_samples
        
        print(f"Created {len(combined)} high-quality samples")
        return combined
    
    def create_low_quality_dataset(self) -> List[Dict]:
        """
        Create low_quality.jsonl with INTENTIONAL issues.
        
        This simulates real-world messy datasets by introducing:
        - Duplicates (copied from real datasets)
        - Missing fields (real issue)
        - Empty responses (real issue)
        - Near-duplicates (real issue)
        """
        print("\n=== Creating low_quality dataset (with intentional issues) ===")
        
        # Start with real samples
        real_samples = self.download_alpaca_sample(10)
        
        samples = []
        
        # Add real samples
        samples.extend(real_samples)
        
        # Add exact duplicates (16% of 24 = ~4 duplicates)
        samples.append(real_samples[0])  # Exact duplicate
        samples.append(real_samples[1])  # Exact duplicate
        samples.append(real_samples[2])  # Exact duplicate
        samples.append(real_samples[3])  # Exact duplicate
        
        # Add near-duplicates (slightly modified)
        samples.append({
            "instruction": "Give three tips for staying healthy.",
            "response": "Here are three tips: 1. Eat healthy food, 2. Exercise often, 3. Sleep well."
        })
        
        samples.append({
            "instruction": "Give three tips for staying healthy.",
            "response": "Three health tips: maintain good diet, exercise regularly, get enough sleep."
        })
        
        # Add missing fields
        samples.append({
            "instruction": "What is machine learning?",
            # Missing "response" field
        })
        
        samples.append({
            # Missing "instruction" field
            "response": "Machine learning is a subset of AI."
        })
        
        # Add empty response
        samples.append({
            "instruction": "Explain quantum computing",
            "response": ""
        })
        
        # Add very short response
        samples.append({
            "instruction": "What is AI?",
            "response": "AI is artificial intelligence."
        })
        
        # Add off-topic samples
        samples.append({
            "instruction": "Explain gradient descent",
            "response": "When a model learns the training data too well and fails on test data."
        })
        
        samples.append({
            "instruction": "What is overfitting?",
            "response": "Gradient descent is an optimization algorithm."
        })
        
        print(f"Created {len(samples)} samples with intentional issues")
        return samples
    
    def create_edge_cases_dataset(self) -> List[Dict]:
        """Create edge_cases.jsonl with boundary conditions."""
        print("\n=== Creating edge_cases dataset ===")
        
        samples = [
            # Very short instruction
            {
                "instruction": "Hi",
                "response": "Hello! How can I help you today?"
            },
            # Very long instruction
            {
                "instruction": "Explain the concept of recursion in programming, including base cases, recursive cases, stack overflow, tail recursion, and provide examples in Python, JavaScript, and Java, and discuss when to use recursion vs iteration.",
                "response": "Recursion is a programming technique where a function calls itself to solve smaller instances of the same problem. A recursive function needs a base case (when to stop) and a recursive case (how to break down the problem). Stack overflow occurs when recursion goes too deep. Tail recursion optimizes this. Examples: Python uses sys.setrecursionlimit(), JavaScript has tail call optimization in ES6, Java has no tail optimization. Use recursion for problems with natural recursive structure (tree traversal, Fibonacci), iteration for performance-critical code."
            },
            # Very short response
            {
                "instruction": "What is 2+2?",
                "response": "4"
            },
            # Very long response
            {
                "instruction": "Explain the French Revolution in detail.",
                "response": "The French Revolution (1789-1799) was a pivotal period that transformed France from an absolute monarchy to a republic. Key causes included: financial crisis from wars and royal spending, social inequality (Three Estates system), Enlightenment ideas challenging monarchical authority, and poor harvests causing famine. Major events: Estates-General convened May 1789, Tennis Court Oath June 1789, Storming of the Bastille July 14 1789, Declaration of the Rights of Man and Citizen August 1789, Women's March on Versailles October 1789, Civil Constitution of the Clergy July 1790, Flight to Varennes June 1791, Champ de Mars Massacre July 1791, Legislative Assembly 1791-1792, Insurrection of August 10 1792, September Massacres 1792, National Convention 1792-1795, Execution of Louis XVI January 1793, Reign of Terror 1793-1794 led by Robespierre, Thermidorian Reaction July 1794, Directory 1795-1799, Coup of 18 Brumaire November 1799 bringing Napoleon to power. Long-term impacts: spread of republican ideals, Napoleonic Code, secularization, rise of nationalism, influence on later revolutions."
            },
            # Empty instruction
            {
                "instruction": "",
                "response": "This is a response without an instruction."
            },
            # Empty response
            {
                "instruction": "Explain photosynthesis",
                "response": ""
            },
            # Unicode content
            {
                "instruction": "What is the chemical formula for water?",
                "response": "The chemical formula for water is H₂O. It consists of two hydrogen atoms and one oxygen atom. In Chinese: 水. In Japanese: 水 (mizu)."
            },
            # Special characters
            {
                "instruction": "Write code with special chars: @#$%^&*()",
                "response": "Special characters in code: @ for decorators in Python, $ for variables in bash, ^ for XOR or start in regex, & for bitwise AND, * for multiplication or unpacking, () for function calls or grouping."
            },
            # Numbers and math
            {
                "instruction": "Solve: ∫x²dx",
                "response": "∫x²dx = x³/3 + C, where C is the constant of integration."
            },
            # Code in response
            {
                "instruction": "Write a Hello World program",
                "response": "Python:\nprint('Hello, World!')\n\nJavaScript:\nconsole.log('Hello, World!');\n\nJava:\npublic class HelloWorld {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n    }\n}"
            },
            # Multiple paragraphs
            {
                "instruction": "Compare supervised and unsupervised learning.",
                "response": "Supervised learning uses labeled data where the model learns to map inputs to known outputs. Examples include classification and regression. The model is trained on a dataset where each example has a known answer.\n\nUnsupervised learning works with unlabeled data, finding hidden patterns or structures. Examples include clustering (grouping similar data) and dimensionality reduction (simplifying data while preserving information).\n\nKey differences: supervised needs labeled data (expensive), unsupervised doesn't; supervised has clear success metrics, unsupervised is more exploratory."
            },
            # Single word response
            {
                "instruction": "What is the opposite of hot?",
                "response": "Cold."
            },
            # Question as response
            {
                "instruction": "Explain gravity",
                "response": "What is gravity? Gravity is the force that attracts objects with mass toward each other."
            },
            # Mixed languages (acceptable in some contexts)
            {
                "instruction": "Translate 'Hello' to Spanish",
                "response": "Hello in Spanish is 'Hola'. In French it's 'Bonjour'. In German it's 'Guten Tag'."
            },
            # Lists and formatting
            {
                "instruction": "List the planets in our solar system",
                "response": "1. Mercury\n2. Venus\n3. Earth\n4. Mars\n5. Jupiter\n6. Saturn\n7. Uranus\n8. Neptune\n\nNote: Pluto was reclassified as a dwarf planet in 2006."
            },
            # Very technical
            {
                "instruction": "Explain transformer attention mechanism mathematically",
                "response": "Attention(Q, K, V) = softmax(QK^T/√d_k)V where Q (query), K (key), V (value) are matrices. Multi-head attention runs h parallel attention layers: MultiHead(Q,K,V) = Concat(head_1,...,head_h)W^O where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V). This allows the model to attend to information from different representation subspaces at different positions."
            },
            # Very basic
            {
                "instruction": "What color is the sky?",
                "response": "The sky appears blue during the day due to Rayleigh scattering, where shorter blue wavelengths are scattered more than red wavelengths. At sunrise/sunset, it appears red/orange because light travels through more atmosphere."
            }
        ]
        
        print(f"Created {len(samples)} edge case samples")
        return samples
    
    def save_jsonl(self, samples: List[Dict], filename: str):
        """Save samples as JSONL file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample) + '\n')
        print(f"Saved {len(samples)} samples to {filepath}")
    
    def download_all(self):
        """Download all dataset samples."""
        print("=" * 60)
        print("DOWNLOADING REAL DATASET SAMPLES")
        print("=" * 60)
        
        # Create high quality dataset
        high_quality = self.create_high_quality_dataset()
        self.save_jsonl(high_quality, "high_quality/sample.jsonl")
        
        # Create low quality dataset
        low_quality = self.create_low_quality_dataset()
        self.save_jsonl(low_quality, "low_quality/sample.jsonl")
        
        # Create edge cases dataset
        edge_cases = self.create_edge_cases_dataset()
        self.save_jsonl(edge_cases, "edge_cases/sample.jsonl")
        
        print("\n" + "=" * 60)
        print("DOWNLOAD COMPLETE")
        print("=" * 60)
        print(f"\nDatasets saved to: {self.output_dir}")
        print("\nNOTE: Some datasets may use fallback samples if")
        print("      network download fails. Fallbacks are based on")
        print("      real dataset patterns from official sources.")


def main():
    """Main entry point."""
    # Output directory relative to this script
    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "datasets"
    
    downloader = RealDatasetDownloader(output_dir)
    downloader.download_all()


if __name__ == "__main__":
    main()