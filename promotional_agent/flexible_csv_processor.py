"""
Flexible CSV Processor - Handles any CSV format with AI-powered schema detection
"""

import pandas as pd
import json
from typing import Dict, List, Tuple, Optional
from openai import OpenAI
import os

class FlexibleCSVProcessor:
    """AI-powered flexible CSV processor"""
    
    EXPECTED_SCHEMAS = {
        'items': ['item_id', 'item_name', 'category', 'subcategory', 'brand', 'price', 
                  'original_price', 'discount_percentage', 'stock_quantity', 'description',
                  'seasonal_relevance', 'festival_relevance', 'region_popular', 
                  'specifications', 'keywords'],
        'users': ['user_id', 'name', 'age', 'age_group', 'gender', 'region', 'city', 
                  'state', 'phone', 'email', 'registration_date', 'total_purchases',
                  'last_purchase_date', 'favorite_categories', 'preferred_language', 
                  'loyalty_points'],
        'purchase_history': ['purchase_id', 'user_id', 'item_id', 'purchase_date', 
                            'quantity', 'total_amount', 'payment_method', 'rating', 'review']
    }
    
    CRITICAL_FIELDS = {
        'items': ['item_id', 'item_name', 'price'],
        'users': ['user_id', 'name'],
        'purchase_history': ['user_id', 'item_id']
    }
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def detect_csv_schema(self, df: pd.DataFrame, csv_type: str) -> Dict:
        """Detect CSV schema and propose column mapping"""
        
        user_columns = df.columns.tolist()
        sample_data = df.head(3).to_dict('records')
        expected_fields = self.EXPECTED_SCHEMAS.get(csv_type, [])
        
        prompt = f"""Analyze this CSV and map columns to expected schema.

CSV Type: {csv_type}
User's Columns: {user_columns}
Sample Data: {json.dumps(sample_data, default=str)}

Expected Fields: {expected_fields}

Return ONLY a JSON object with this structure:
{{
  "mappings": {{
    "expected_field": "user_column_name",
    ...
  }},
  "confidence": {{
    "expected_field": 0.95,
    ...
  }},
  "missing_fields": ["field1", "field2"],
  "unknown_columns": ["col1", "col2"]
}}

Rules:
- Map user columns to expected fields based on semantic similarity
- Use confidence 0-1 (1=perfect match, 0.5+=probable, <0.5=uncertain)
- List fields with no mapping in missing_fields
- List user columns that couldn't be mapped in unknown_columns
- Return valid JSON only, no explanation"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            result['csv_type'] = csv_type
            result['total_columns'] = len(user_columns)
            result['mapped_count'] = len(result.get('mappings', {}))
            
            return result
        except Exception as e:
            return {
                'mappings': {},
                'confidence': {},
                'missing_fields': expected_fields,
                'unknown_columns': user_columns,
                'error': str(e)
            }
    
    def generate_missing_data(self, df: pd.DataFrame, mapping: Dict, 
                             missing_fields: List[str], csv_type: str) -> pd.DataFrame:
        """Generate synthetic data for missing critical fields using AI"""
        
        result_df = df.copy()
        
        for field in missing_fields:
            if field not in self.CRITICAL_FIELDS.get(csv_type, []):
                # Generate based on field type
                if field in ['item_id', 'user_id', 'purchase_id']:
                    result_df[field] = [f"{field.split('_')[0].upper()}{str(i).zfill(4)}" 
                                       for i in range(len(df))]
                elif 'date' in field.lower():
                    result_df[field] = pd.Timestamp.now().strftime('%Y-%m-%d')
                elif field in ['age', 'quantity', 'total_purchases', 'loyalty_points', 'stock_quantity']:
                    result_df[field] = 0
                elif field in ['discount_percentage']:
                    result_df[field] = 0.0
                elif field in ['price', 'original_price', 'total_amount']:
                    result_df[field] = 100.0
                else:
                    # Use AI for complex fields
                    result_df[field] = self._generate_field_with_ai(df, field, csv_type)
        
        return result_df
    
    def _generate_field_with_ai(self, df: pd.DataFrame, field: str, csv_type: str) -> List:
        """Use AI to generate intelligent values for a field"""
        
        sample = df.head(5).to_dict('records')
        
        prompt = f"""Generate values for missing field '{field}' in {csv_type} data.

Sample existing data: {json.dumps(sample, default=str)}

Generate {len(df)} values for field '{field}' that are:
- Contextually relevant to existing data
- Realistic for Indian retail business
- Diverse and appropriate

Return as JSON array: ["value1", "value2", ...]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            values = json.loads(response.choices[0].message.content)
            return values[:len(df)] + [''] * (len(df) - len(values))
        except:
            return ['N/A'] * len(df)
    
    def transform_dataframe(self, df: pd.DataFrame, mapping: Dict, 
                           missing_fields: List[str], csv_type: str) -> pd.DataFrame:
        """Transform dataframe using column mapping and generate missing data"""
        
        # Create new dataframe with mapped columns
        transformed = pd.DataFrame()
        
        # Map existing columns
        for expected_field, user_column in mapping.items():
            if user_column in df.columns:
                transformed[expected_field] = df[user_column]
        
        # Generate missing fields
        transformed = self.generate_missing_data(transformed, mapping, missing_fields, csv_type)
        
        # Add unmapped original columns as metadata
        unmapped = [col for col in df.columns if col not in mapping.values()]
        for col in unmapped:
            transformed[f"_original_{col}"] = df[col]
        
        return transformed
    
    def validate_critical_fields(self, df: pd.DataFrame, csv_type: str) -> Tuple[bool, List[str]]:
        """Check if critical fields exist or can be generated"""
        
        critical = self.CRITICAL_FIELDS.get(csv_type, [])
        missing = [f for f in critical if f not in df.columns]
        
        return len(missing) == 0, missing
    
    def auto_convert_types(self, df: pd.DataFrame, csv_type: str) -> pd.DataFrame:
        """Automatically convert column data types"""
        
        result = df.copy()
        
        # Numeric fields
        numeric_fields = ['price', 'original_price', 'discount_percentage', 'age', 
                         'quantity', 'total_amount', 'loyalty_points', 'total_purchases',
                         'stock_quantity', 'rating']
        
        for field in numeric_fields:
            if field in result.columns:
                result[field] = pd.to_numeric(result[field], errors='coerce').fillna(0)
        
        # Date fields
        date_fields = ['purchase_date', 'registration_date', 'last_purchase_date']
        for field in date_fields:
            if field in result.columns:
                result[field] = pd.to_datetime(result[field], errors='coerce')
        
        return result
    
    def get_schema_summary(self, detection_result: Dict) -> str:
        """Generate human-readable schema summary"""
        
        mapped = detection_result.get('mapped_count', 0)
        total = detection_result.get('total_columns', 0)
        missing = len(detection_result.get('missing_fields', []))
        
        summary = f"✅ Mapped: {mapped}/{total} columns\n"
        
        if missing > 0:
            summary += f"⚠️ Missing: {missing} fields (will be auto-generated)\n"
        
        high_conf = sum(1 for c in detection_result.get('confidence', {}).values() if c > 0.8)
        if high_conf > 0:
            summary += f"🎯 High confidence mappings: {high_conf}\n"
        
        return summary
