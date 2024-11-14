from openai import OpenAI
import os
from typing import Dict, Any, List
from data.loadData import ProductDataLoader
from function.formatProduct import ProductFormatter
from function.findProduct import ProductFinder
from function.basicSearch import BasicSearcher
from function.analyzeQuery import QueryAnalyzer

class ProductDetails:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.data_loader = ProductDataLoader()
        self.formatter = ProductFormatter()
        self.finder = ProductFinder(client=self.client)
        self.basic_searcher = BasicSearcher()
        self.query_analyzer = QueryAnalyzer(self.client)

        # Initialize data
        self.products_data: List[Dict[str, Any]] = []
        self.product_names: List[str] = []
        self.refresh_data()

    def refresh_data(self) -> bool:
        """Refresh product data from database"""
        try:
            self.products_data, self.product_names = self.data_loader.load_product_data()
            return bool(self.products_data)
        except Exception as e:
            print(f"Error refreshing data: {str(e)}")
            return False

    def get_product_info(self, query: str) -> str:
        """Main method to handle product queries"""
        try:
            if not self.products_data:
                if not self.refresh_data():
                    return "Unable to access product data. Please try again later."

            print(f"Processing product query: {query}")
            print(f"Total products loaded: {len(self.products_data)}")

             # Sample first product for debugging
            if self.products_data:
                print(f"Sample product data: {self.products_data[0]}")

            query_type, value = self.query_analyzer.analyze_query(query)
            print(f"Query type: {query_type}, Value: {value}")
            
            query_type, value = self.query_analyzer.analyze_query(query)
            print(f"Searching for: {value}")

            if not query_type or not value:
                return "I couldn't understand your query. Please provide a SKU number or describe the product you're looking for."

            print("Available products in database:")

            if query_type == "SKU":
                product = self.finder.find_product_by_sku(self.products_data, value)
                if product:
                    return self.formatter.format_product_details(product)
                return f"No product found with SKU: {value}"

            if query_type == "PRODUCT":
                # Debug print
                print(f"Total products in database: {len(self.products_data)}")
                print(f"Total product names: {len(self.product_names)}")

                matching_products = self.finder.find_matching_products(
                    value,
                    self.products_data,
                    self.product_names,
                    self.basic_searcher
                )

                if not matching_products:
                    return f"No products found matching '{value}'"

                return self.formatter.format_product_list(matching_products, self.products_data)

            return "I couldn't understand your query. Please try again with a SKU number or product description."

        except Exception as e:
            print(f"Error in get_product_info: {str(e)}")
        return "Sorry, there was an error processing your request. Please try again."