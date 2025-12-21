"""
Retail Data Processor - Processes CSV files and creates document chunks for vector store
"""

import pandas as pd
from typing import List, Dict
import json


class RetailDataProcessor:
    """Process retail CSV data and create document chunks"""
    
    def __init__(self):
        self.chunk_size = 1500
        self.business_images = {}
    
    def process_retail_data(
        self, 
        items_df: pd.DataFrame,
        users_df: pd.DataFrame,
        purchase_history_df: pd.DataFrame
    ) -> List[Dict]:
        """Process all retail data and create document chunks"""
        
        chunks = []
        
        # Process items
        chunks.extend(self._process_items(items_df))
        
        # Process users
        chunks.extend(self._process_users(users_df))
        
        # Process purchase history with relationships
        chunks.extend(self._process_purchase_history(
            purchase_history_df, 
            items_df, 
            users_df
        ))
        
        # Create aggregate insights
        chunks.extend(self._create_insights(
            items_df,
            users_df,
            purchase_history_df
        ))
        
        return chunks
    
    def _process_items(self, items_df: pd.DataFrame) -> List[Dict]:
        """Create chunks for item data with flexible column support"""
        chunks = []
        
        def safe_get(row, col, default='N/A'):
            return row.get(col, default) if col in items_df.columns else default
        
        for _, item in items_df.iterrows():
            # Create detailed item description
            item_text = f"""
ITEM: {safe_get(item, 'item_name')} ({safe_get(item, 'item_id')})

Category: {safe_get(item, 'category')} - {safe_get(item, 'subcategory')}
Brand: {safe_get(item, 'brand')}

Pricing:
- Current Price: ₹{safe_get(item, 'price')}
- Original Price: ₹{safe_get(item, 'original_price')}
- Discount: {safe_get(item, 'discount_percentage')}% OFF

Stock: {safe_get(item, 'stock_quantity')} units available

Description: {safe_get(item, 'description')}

Seasonal Relevance: {safe_get(item, 'seasonal_relevance')}
Festival Relevance: {safe_get(item, 'festival_relevance')}
Popular in Regions: {safe_get(item, 'region_popular')}

Specifications: {safe_get(item, 'specifications')}
Keywords: {safe_get(item, 'keywords')}

PROMOTIONAL ANGLE: This item offers great value with {safe_get(item, 'discount_percentage')}% discount. 
Perfect for {safe_get(item, 'festival_relevance')} celebrations and suitable for {safe_get(item, 'seasonal_relevance')} season.
Popular among customers in {safe_get(item, 'region_popular')} regions.
"""
            
            chunks.append({
                "text": item_text.strip(),
                "metadata": {
                    "type": "item",
                    "item_id": item['item_id'],
                    "item_name": item['item_name'],
                    "category": item['category'],
                    "brand": item['brand'],
                    "price": float(item['price']),
                    "discount": float(item['discount_percentage'])
                }
            })
        
        return chunks
    
    def _process_users(self, users_df: pd.DataFrame) -> List[Dict]:
        """Create chunks for user data with flexible column support"""
        chunks = []
        
        def safe_get(row, col, default='N/A'):
            return row.get(col, default) if col in users_df.columns else default
        
        for _, user in users_df.iterrows():
            user_text = f"""
CUSTOMER PROFILE: {safe_get(user, 'name')} ({safe_get(user, 'user_id')})

Demographics:
- Age: {safe_get(user, 'age')} years ({safe_get(user, 'age_group')} age group)
- Gender: {safe_get(user, 'gender')}
- Location: {safe_get(user, 'city')}, {safe_get(user, 'state')} ({safe_get(user, 'region')} region)
- Preferred Language: {safe_get(user, 'preferred_language')}

Shopping Behavior:
- Total Purchases: {safe_get(user, 'total_purchases')}
- Last Purchase: {safe_get(user, 'last_purchase_date')}
- Loyalty Points: {safe_get(user, 'loyalty_points')}
- Favorite Categories: {safe_get(user, 'favorite_categories')}

Contact: {safe_get(user, 'email')}, {safe_get(user, 'phone')}
Member Since: {safe_get(user, 'registration_date')}

MARKETING NOTES: 
- Target this customer with products from: {safe_get(user, 'favorite_categories')}
- Use {safe_get(user, 'preferred_language')} language for communication
- Customer is from {safe_get(user, 'region')} region, {safe_get(user, 'city')} city
"""
            
            chunks.append({
                "text": user_text.strip(),
                "metadata": {
                    "type": "user",
                    "user_id": user['user_id'],
                    "name": user['name'],
                    "age_group": user['age_group'],
                    "region": user['region'],
                    "preferred_language": user['preferred_language']
                }
            })
        
        return chunks
    
    def _process_purchase_history(
        self,
        history_df: pd.DataFrame,
        items_df: pd.DataFrame,
        users_df: pd.DataFrame
    ) -> List[Dict]:
        """Create chunks for purchase history with context"""
        chunks = []
        
        # Group by user for history
        for user_id, user_purchases in history_df.groupby('user_id'):
            # Get user info
            user_info = users_df[users_df['user_id'] == user_id].iloc[0] if len(users_df[users_df['user_id'] == user_id]) > 0 else None
            
            if user_info is None:
                continue
            
            # Create purchase history text
            history_text = f"""
PURCHASE HISTORY FOR: {user_info['name']} ({user_id})

Customer Profile: {user_info['age']} years, {user_info['gender']}, from {user_info['city']}
Total Purchases: {len(user_purchases)}

Recent Purchase Details:
"""
            
            # Add last 5 purchases with item details
            recent_purchases = user_purchases.sort_values('purchase_date', ascending=False).head(5)
            
            for _, purchase in recent_purchases.iterrows():
                item_info = items_df[items_df['item_id'] == purchase['item_id']].iloc[0] if len(items_df[items_df['item_id'] == purchase['item_id']]) > 0 else None
                
                if item_info is not None:
                    history_text += f"""
- {purchase['purchase_date']}: {item_info['item_name']} ({item_info['category']})
  * Quantity: {purchase['quantity']}, Amount: ₹{purchase['total_amount']}
  * Rating: {purchase['rating']}/5
  * Review: {purchase['review']}
"""
            
            # Add insights
            categories_bought = []
            total_spent = user_purchases['total_amount'].sum()
            avg_rating = user_purchases['rating'].mean()
            
            for _, purchase in user_purchases.iterrows():
                item = items_df[items_df['item_id'] == purchase['item_id']]
                if len(item) > 0:
                    categories_bought.append(item.iloc[0]['category'])
            
            unique_categories = list(set(categories_bought))
            
            history_text += f"""

INSIGHTS:
- Total Spent: ₹{total_spent:,.2f}
- Average Rating Given: {avg_rating:.1f}/5
- Categories Purchased: {', '.join(unique_categories)}
- Most Active Region: {user_info['region']}
- Preferred Payment: {user_purchases['payment_method'].mode()[0] if len(user_purchases) > 0 else 'Unknown'}

RECOMMENDATION STRATEGY:
- Customer shows interest in: {', '.join(unique_categories)}
- Target with similar products
- Customer is {'highly satisfied' if avg_rating >= 4.5 else 'satisfied' if avg_rating >= 3.5 else 'moderately satisfied'}
- Location-based offers for {user_info['city']} region
"""
            
            chunks.append({
                "text": history_text.strip(),
                "metadata": {
                    "type": "purchase_history",
                    "user_id": user_id,
                    "total_purchases": len(user_purchases),
                    "total_spent": float(total_spent),
                    "avg_rating": float(avg_rating)
                }
            })
        
        return chunks
    
    def _create_insights(
        self,
        items_df: pd.DataFrame,
        users_df: pd.DataFrame,
        history_df: pd.DataFrame
    ) -> List[Dict]:
        """Create aggregate business insights"""
        chunks = []
        
        # Top items
        item_sales = history_df.groupby('item_id').agg({
            'quantity': 'sum',
            'total_amount': 'sum',
            'rating': 'mean'
        }).sort_values('total_amount', ascending=False).head(10)
        
        top_items_text = "TOP 10 BEST SELLING ITEMS:\n\n"
        
        for item_id, stats in item_sales.iterrows():
            item_info = items_df[items_df['item_id'] == item_id]
            if len(item_info) > 0:
                item = item_info.iloc[0]
                top_items_text += f"""
{item['item_name']} ({item['brand']})
- Category: {item['category']}
- Total Units Sold: {int(stats['quantity'])}
- Revenue: ₹{stats['total_amount']:,.2f}
- Average Rating: {stats['rating']:.1f}/5
- Current Discount: {item['discount_percentage']}%
"""
        
        chunks.append({
            "text": top_items_text.strip(),
            "metadata": {
                "type": "insight",
                "insight_type": "top_items"
            }
        })
        
        # Regional preferences
        regional_text = "REGIONAL BUYING PREFERENCES:\n\n"
        
        for region in users_df['region'].unique():
            region_users = users_df[users_df['region'] == region]['user_id'].tolist()
            region_purchases = history_df[history_df['user_id'].isin(region_users)]
            
            if len(region_purchases) > 0:
                # Get top categories
                region_items = []
                for item_id in region_purchases['item_id'].unique():
                    item = items_df[items_df['item_id'] == item_id]
                    if len(item) > 0:
                        region_items.append(item.iloc[0]['category'])
                
                from collections import Counter
                top_categories = Counter(region_items).most_common(3)
                
                regional_text += f"""
{region} Region:
- Total Customers: {len(region_users)}
- Total Purchases: {len(region_purchases)}
- Top Categories: {', '.join([cat for cat, _ in top_categories])}
- Average Spend: ₹{region_purchases['total_amount'].mean():,.2f}
"""
        
        chunks.append({
            "text": regional_text.strip(),
            "metadata": {
                "type": "insight",
                "insight_type": "regional_preferences"
            }
        })
        
        # Seasonal insights
        seasonal_text = "SEASONAL PRODUCT OPPORTUNITIES:\n\n"
        
        for season in items_df['seasonal_relevance'].unique():
            seasonal_items = items_df[items_df['seasonal_relevance'] == season]
            
            if len(seasonal_items) > 0:
                seasonal_text += f"""
{season} Season:
- Available Products: {len(seasonal_items)}
- Categories: {', '.join(seasonal_items['category'].unique())}
- Average Discount: {seasonal_items['discount_percentage'].mean():.1f}%
- Top Brands: {', '.join(seasonal_items['brand'].value_counts().head(3).index.tolist())}
"""
        
        chunks.append({
            "text": seasonal_text.strip(),
            "metadata": {
                "type": "insight",
                "insight_type": "seasonal"
            }
        })
        
        # Festival insights
        festival_items = items_df[items_df['festival_relevance'].notna() & (items_df['festival_relevance'] != 'None')]
        
        if len(festival_items) > 0:
            festival_text = "FESTIVAL-SPECIFIC PRODUCT RECOMMENDATIONS:\n\n"
            
            for festival in festival_items['festival_relevance'].unique():
                if festival and festival != 'None':
                    festival_prods = items_df[items_df['festival_relevance'].str.contains(festival, na=False)]
                    
                    festival_text += f"""
{festival}:
- Available Products: {len(festival_prods)}
- Categories: {', '.join(festival_prods['category'].unique())}
- Average Discount: {festival_prods['discount_percentage'].mean():.1f}%
- Price Range: ₹{festival_prods['price'].min():.0f} - ₹{festival_prods['price'].max():.0f}
"""
            
            chunks.append({
                "text": festival_text.strip(),
                "metadata": {
                    "type": "insight",
                    "insight_type": "festival"
                }
            })
        
        return chunks
    
    def process_business_images(self, business_id: str, image_files: List) -> List[Dict]:
        """Process uploaded images for a business"""
        from document_processor import DocumentProcessor
        import tempfile
        import os
        
        doc_processor = DocumentProcessor()
        chunks = []
        
        for image_file in image_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(image_file.getvalue())
                tmp_path = tmp.name
            
            try:
                img_chunks = doc_processor.process_document(tmp_path)
                for chunk in img_chunks:
                    chunk['metadata']['business_id'] = business_id
                    chunk['metadata']['image_name'] = image_file.name
                chunks.extend(img_chunks)
            finally:
                os.unlink(tmp_path)
        
        self.business_images[business_id] = len(chunks)
        return chunks
    
    def _get_loyalty_tier(self, points: int) -> str:
        """Determine loyalty tier based on points"""
        if points >= 5000:
            return "Platinum"
        elif points >= 3000:
            return "Gold"
        elif points >= 1000:
            return "Silver"
        else:
            return "Bronze"
