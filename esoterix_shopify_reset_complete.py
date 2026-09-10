#!/usr/bin/env python3
"""
🔥 RESET COMPLET SHOPIFY - VERSION SIMPLIFIÉE
Sauvegarde → Supprime tous les produits → Recrée proprement depuis Esoterix
⚠️ SUPPRESSION AUTOMATIQUE (pas de confirmation interactive)
"""

import os
import json
import requests
import logging
import csv
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ShopifyBackup:
    """Sauvegarde les produits Shopify avant suppression"""
    
    def __init__(self, shop_name: str, access_token: str):
        self.shop_name = shop_name
        self.access_token = access_token
        self.api_url = f"https://{shop_name}.myshopify.com/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
    
    def backup_all_products(self) -> str:
        """Exporte tous les produits en CSV"""
        try:
            logger.info("💾 SAUVEGARDE EN COURS...")
            
            products = []
            limit = 250
            after = None
            total = 0
            
            while True:
                params = {"limit": limit}
                if after:
                    params["after"] = after
                
                response = requests.get(
                    f"{self.api_url}/products.json",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Erreur API: {response.text}")
                    break
                
                data = response.json()
                batch_products = data.get('products', [])
                products.extend(batch_products)
                total = len(products)
                
                logger.info(f"📊 {total} produits téléchargés...")
                
                if len(batch_products) < limit:
                    break
                
                # Pagination
                last_product = batch_products[-1]
                after = last_product.get('id')
            
            # Sauvegarder en CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_shopify_{self.shop_name}_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'title', 'handle', 'vendor', 'type', 'images_count', 'variants_count'])
                writer.writeheader()
                
                for product in products:
                    writer.writerow({
                        'id': product.get('id'),
                        'title': product.get('title'),
                        'handle': product.get('handle'),
                        'vendor': product.get('vendor'),
                        'type': product.get('product_type'),
                        'images_count': len(product.get('images', [])),
                        'variants_count': len(product.get('variants', []))
                    })
            
            logger.info(f"✅ SAUVEGARDE COMPLÈTE: {filename}")
            logger.info(f"📊 Total: {total} produits sauvegardés")
            return filename
        
        except Exception as e:
            logger.error(f"❌ Erreur sauvegarde: {e}")
            return None


class ShopifyDeleter:
    """Supprime tous les produits Shopify"""
    
    def __init__(self, shop_name: str, access_token: str):
        self.shop_name = shop_name
        self.access_token = access_token
        self.api_url = f"https://{shop_name}.myshopify.com/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        self.deleted_count = 0
    
    def get_all_product_ids(self) -> List[int]:
        """Récupère les IDs de tous les produits"""
        product_ids = []
        limit = 250
        after = None
        
        try:
            while True:
                params = {"limit": limit}
                if after:
                    params["after"] = after
                
                response = requests.get(
                    f"{self.api_url}/products.json",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"❌ Erreur API: {response.text}")
                    break
                
                data = response.json()
                batch_products = data.get('products', [])
                
                if not batch_products:
                    break
                
                for product in batch_products:
                    product_ids.append(product['id'])
                
                logger.info(f"📋 IDs récupérés: {len(product_ids)}")
                
                if len(batch_products) < limit:
                    break
                
                after = batch_products[-1].get('id')
            
            return product_ids
        except Exception as e:
            logger.error(f"❌ Erreur récupération IDs: {e}")
            return []
    
    def delete_all_products(self) -> bool:
        """Supprime tous les produits"""
        try:
            product_ids = self.get_all_product_ids()
            
            if not product_ids:
                logger.error("❌ Aucun produit trouvé")
                return False
            
            logger.warning(f"🔴 {len(product_ids)} produits à supprimer")
            logger.warning("🔥 SUPPRESSION EN COURS...")
            
            for i, product_id in enumerate(product_ids, 1):
                try:
                    response = requests.delete(
                        f"{self.api_url}/products/{product_id}.json",
                        headers=self.headers
                    )
                    
                    if response.status_code == 200:
                        self.deleted_count += 1
                        if i % 100 == 0:
                            logger.info(f"🗑️  {i}/{len(product_ids)} produits supprimés...")
                    else:
                        logger.warning(f"⚠️  Erreur suppression {product_id}: {response.text}")
                    
                    # Rate limiting
                    time.sleep(0.1)
                
                except Exception
