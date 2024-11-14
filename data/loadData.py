import os
import requests
from typing import Dict, Any, List, Tuple

class ProductDataLoader:
    def __init__(self):
        self.api_url = os.environ.get('API_URL')
        self.request_id = os.environ.get('REQUEST_ID')
        self.token = os.environ.get('TOKEN')

    def fetch_data(self) -> Dict[str, Any]:
        """
        Fetch SKU data from the API
        Returns:
            Dict containing the API response
        """
        payload = {
            "RequestID": self.request_id,
            "RequestCode": "GTALLSKU",
            "Token": self.token
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return {}

    def extract_products(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract product data from the API response
        Args:
            data: Raw API response
        Returns:
            List of product dictionaries from link_return_request
        """
        try:
            return data['Response']['RespondStatus']['ReturnData']['link_return_request']
        except KeyError as e:
            print(f"Error extracting products: {e}")
            return []

    def process_product_names(self, products: List[Dict[str, Any]]) -> List[Dict[str, str]]:
      """Process raw product data into a searchable format"""
      processed_products = []
      for product in products:
          processed_product = {
              'sku': product.get('RSkuNo', ''),
              'brand': product.get('RSkuBrnName', ''),
              'name': product.get('RSkuName1', ''),
              'name2': product.get('RSkuName2', ''),
              'name3': product.get('RSkuName3', ''),
              'category': product.get('RSkuPrName', ''),
              'color': product.get('RSkuInkName', ''),
              'price': product.get('RSkuPrice', ''),
              'stock': product.get('RQoh', ''),
              'searchable_text': f"{product.get('RSkuBrnName', '')} {product.get('RSkuName1', '')} {product.get('RSkuName2', '')} {product.get('RSkuName3', '')} {product.get('RSkuPrName', '')} {product.get('RSkuInkName', '')}"
          }
          processed_products.append(processed_product)
      return processed_products


    def load_product_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """
        Load and process all product data
        Returns:
            Tuple containing:
            - List of full product details
            - List of processed product names for search
        """
        try:
            raw_data = self.fetch_data()
            if not raw_data:
                print("No data received from API")
                return [], []

            products = self.extract_products(raw_data)
            if not products:
                print("No products found in API response")
                return [], []

            product_names = self.process_product_names(products)

            print(f"Loaded {len(products)} products")
            return products, product_names

        except Exception as e:
            print(f"Error loading product data: {e}")
            return [], []

    def get_product_by_sku(self, sku: str) -> Dict[str, Any]:
        """
        Get a specific product by SKU
        Args:
            sku: Product SKU number
        Returns:
            Product dictionary or empty dict if not found
        """
        products, _ = self.load_product_data()
        return next((product for product in products if product['RSkuNo'] == sku), {})

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """
        Search products by query string across all relevant fields
        Args:
            query: Search query
        Returns:
            List of matching products
        """
        products, product_names = self.load_product_data()
        query = query.lower()

        matches = []
        for product in product_names:
            # Search across all fields using the combined searchable text
            if query in product['searchable_text'].lower():
                # Get full product details for matches
                full_product = next((p for p in products if p['RSkuNo'] == product['sku']), None)
                if full_product:
                    matches.append(full_product)

        return matches[:5]  # Return top 5 matches