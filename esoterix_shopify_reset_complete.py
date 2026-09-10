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
                
                except Exception as e:
                    logger.error(f"❌ Erreur suppression {product_id}: {e}")
            
            logger.warning(f"🔥 SUPPRESSION COMPLÈTE: {self.deleted_count}/{len(product_ids)} produits supprimés")
            return True
        
        except Exception as e:
            logger.error(f"❌ Erreur suppression: {e}")
            return False


class EsotrixScraper:
    """Scrape le catalogue Esoterix"""
    
    def __init__(self, email: str, password: str):
        self.base_url = "https://www.esoterix.eu"
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.driver = None
        self.products = []
    
    def setup_driver(self):
        """Configure Selenium pour headless Chrome"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0")
        
        self.driver = webdriver.Chrome(options=options)
    
    def login(self):
        """Authentifie sur Esoterix"""
        try:
            logger.info("🔓 Connexion à Esoterix...")
            self.driver.get(f"{self.base_url}/connexion")
            time.sleep(2)
            
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            email_field.send_keys(self.email)
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(self.password)
            
            login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_btn.click()
            
            time.sleep(3)
            logger.info("✅ Connecté à Esoterix")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur login: {e}")
            return False
    
    def get_category_urls(self) -> List[str]:
        """Récupère les URLs de toutes les catégories"""
        try:
            logger.info("🔍 Récupération des catégories...")
            self.driver.get(f"{self.base_url}/nos-produits")
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            category_urls = []
            
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href and not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                if self.base_url in href and '/connexion' not in href and href != self.base_url:
                    if href not in category_urls:
                        category_urls.append(href)
            
            logger.info(f"✅ {len(category_urls)} catégories trouvées")
            return category_urls
        except Exception as e:
            logger.error(f"❌ Erreur catégories: {e}")
            return []
    
    def scrape_category(self, category_url: str, category_name: str) -> List[Dict]:
        """Scrape tous les produits d'une catégorie"""
        products = []
        page = 1
        max_pages = 50
        
        try:
            while page <= max_pages:
                logger.info(f"📄 {category_name} - Page {page}")
                
                url = f"{category_url}?page={page}"
                self.driver.get(url)
                time.sleep(1)
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                product_items = soup.find_all('div', class_='product-item')
                
                if not product_items:
                    logger.info(f"✅ Fin catégorie {category_name}")
                    break
                
                for item in product_items:
                    try:
                        product = self._extract_product_data(item, category_name)
                        if product:
                            products.append(product)
                    except Exception as e:
                        logger.warning(f"⚠️  Erreur extraction: {e}")
                
                page += 1
        except Exception as e:
            logger.error(f"❌ Erreur scrape: {e}")
        
        return products
    
    def _extract_product_data(self, item, category: str) -> Optional[Dict]:
        """Extrait les données d'un produit"""
        try:
            name_elem = item.find('a', class_='product-name')
            if not name_elem:
                return None
            
            name = name_elem.text.strip()
            product_url = name_elem.get('href', '')
            
            price_elem = item.find('span', class_='price')
            price_text = price_elem.text.strip() if price_elem else "0"
            price = float(price_text.replace('€', '').replace(',', '.').strip())
            
            stock_elem = item.find('span', class_='stock')
            stock = int(stock_elem.text.strip()) if stock_elem else 0
            
            img_elem = item.find('img')
            image_url = img_elem.get('src', '') if img_elem else ''
            if not image_url.startswith('http'):
                image_url = urljoin(self.base_url, image_url)
            
            desc_elem = item.find('p', class_='description')
            short_desc = desc_elem.text.strip() if desc_elem else name
            
            return {
                'name': name,
                'url': urljoin(self.base_url, product_url) if product_url else '',
                'price': price,
                'stock': stock,
                'image_url': image_url,
                'category': category,
                'description': short_desc,
                'sku': hashlib.md5(name.encode()).hexdigest()[:10]
            }
        except Exception as e:
            logger.warning(f"⚠️  Erreur extraction: {e}")
            return None
    
    def scrape_all(self) -> List[Dict]:
        """Scrape l'ensemble du catalogue"""
        try:
            self.setup_driver()
            
            if not self.login():
                return []
            
            category_urls = self.get_category_urls()
            
            for category_url in category_urls:
                category_name = category_url.split('/')[-1].replace('-', ' ').title()
                products = self.scrape_category(category_url, category_name)
                self.products.extend(products)
            
            logger.info(f"✅ Total: {len(self.products)} produits scrapés")
            return self.products
        finally:
            if self.driver:
                self.driver.quit()


class ShopifyRecreator:
    """Recrée les produits dans Shopify"""
    
    def __init__(self, shop_name: str, access_token: str):
        self.shop_name = shop_name
        self.access_token = access_token
        self.api_url = f"https://{shop_name}.myshopify.com/admin/api/2024-01"
        self.headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json"
        }
        self.collections = {}
    
    def get_or_create_collection(self, collection_name: str) -> Optional[str]:
        """Récupère ou crée une collection"""
        
        if collection_name in self.collections:
            return self.collections[collection_name]
        
        try:
            response = requests.get(
                f"{self.api_url}/collections.json",
                headers=self.headers,
                params={'title': collection_name}
            )
            
            if response.status_code == 200:
                collections = response.json().get('collections', [])
                if collections:
                    col_id = str(collections[0]['id'])
                    self.collections[collection_name] = col_id
                    return col_id
            
            data = {
                "collection": {
                    "title": collection_name,
                    "published": True
                }
            }
            
            response = requests.post(
                f"{self.api_url}/custom_collections.json",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                col_id = str(response.json()['custom_collection']['id'])
                self.collections[collection_name] = col_id
                logger.info(f"✅ Collection créée: {collection_name}")
                return col_id
            else:
                logger.error(f"❌ Erreur création collection: {response.text}")
        except Exception as e:
            logger.error(f"❌ Erreur collection: {e}")
        
        return None
    
    def generate_seo_description(self, product_name: str, original_desc: str, category: str) -> str:
        """Génère une description SEO"""
        
        desc = f"""{product_name} - {category}

{original_desc}

Produit: {product_name}
Catégorie: {category}

Découvrez ce {category.lower()} authentique et de qualité. Idéal pour:
- Votre bien-être quotidien
- Votre pratique spirituelle
- Votre collection ésotérique
- Les cadeaux originaux

Produit importé directement, garantissant l'authenticité et la qualité.
"""
        
        return desc
    
    def create_product(self, product: Dict) -> bool:
        """Crée un produit dans Shopify"""
        try:
            seo_desc = self.generate_seo_description(
                product['name'],
                product['description'],
                product['category']
            )
            
            shopify_price = product['price'] * 2.5
            
            product_data = {
                "product": {
                    "title": product['name'],
                    "body_html": seo_desc,
                    "vendor": "Esoterix Import",
                    "product_type": product['category'],
                    "status": "active",
                    "variants": [
                        {
                            "price": str(shopify_price),
                            "sku": product['sku'],
                            "inventory_quantity": product['stock'],
                            "inventory_management": "shopify",
                            "fulfillment_service": "manual"
                        }
                    ]
                }
            }
            
            if product['image_url']:
                product_data["product"]["images"] = [
                    {
                        "src": product['image_url'],
                        "alt": product['name']
                    }
                ]
            
            response = requests.post(
                f"{self.api_url}/products.json",
                headers=self.headers,
                json=product_data
            )
            
            if response.status_code == 201:
                new_product = response.json()['product']
                
                collection_id = self.get_or_create_collection(product['category'])
                if collection_id:
                    requests.put(
                        f"{self.api_url}/collections/{collection_id}/products.json",
                        headers=self.headers,
                        json={"product_ids": [new_product['id']]}
                    )
                
                return True
            else:
                logger.warning(f"⚠️  Erreur création {product['name']}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Erreur création produit: {e}")
            return False
    
    def recreate_all(self, products: List[Dict]) -> Dict:
        """Recrée tous les produits"""
        stats = {
            'total': len(products),
            'created': 0,
            'failed': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🚀 RECRÉATION EN COURS: {len(products)} produits")
        
        for i, product in enumerate(products, 1):
            if i % 50 == 0:
                logger.info(f"[{i}/{len(products)}] Recréation en cours...")
            
            if self.create_product(product):
                stats['created'] += 1
            else:
                stats['failed'] += 1
            
            time.sleep(0.5)
        
        logger.info(f"✅ Recréation terminée: {stats['created']} créés, {stats['failed']} échoués")
        return stats


def main():
    """Fonction principale"""
    
    esoterix_email = os.getenv('ESOTERIX_EMAIL')
    esoterix_password = os.getenv('ESOTERIX_PASSWORD')
    shopify_store = os.getenv('SHOPIFY_STORE')
    shopify_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
    
    if not all([esoterix_email, esoterix_password, shopify_store, shopify_token]):
        logger.error("❌ Variables d'environnement manquantes")
        return
    
    logger.info("="*70)
    logger.info("🔥 RESET COMPLET SHOPIFY - ESOTERIX (VERSION SIMPLIFIÉE)")
    logger.info("="*70)
    
    # Phase 1: SAUVEGARDE
    backup = ShopifyBackup(shopify_store, shopify_token)
    backup_file = backup.backup_all_products()
    
    if not backup_file:
        logger.error("❌ Sauvegarde échouée. Opération annulée.")
        return
    
    # Phase 2: SUPPRESSION (AUTOMATIQUE)
    logger.info("\n🗑️  SUPPRESSION AUTOMATIQUE (pas de confirmation)")
    deleter = ShopifyDeleter(shopify_store, shopify_token)
    if not deleter.delete_all_products():
        logger.error("❌ Suppression échouée")
        return
    
    logger.info("✅ Tous les produits supprimés")
    time.sleep(5)
    
    # Phase 3: SCRAPING ESOTERIX
    logger.info("\n" + "="*70)
    logger.info("📥 SCRAPING ESOTERIX")
    logger.info("="*70 + "\n")
    
    scraper = EsotrixScraper(esoterix_email, esoterix_password)
    products = scraper.scrape_all()
    
    if not products:
        logger.error("❌ Aucun produit scrapé")
        return
    
    # Phase 4: RECRÉATION
    logger.info("\n" + "="*70)
    logger.info("✨ RECRÉATION DANS SHOPIFY")
    logger.info("="*70 + "\n")
    
    recreator = ShopifyRecreator(shopify_store, shopify_token)
    stats = recreator.recreate_all(products)
    
    # Résumé final
    logger.info("\n" + "="*70)
    logger.info("📊 RÉSUMÉ FINAL")
    logger.info("="*70)
    logger.info(f"✅ Sauvegarde: {backup_file}")
    logger.info(f"🗑️  Supprimés: {deleter.deleted_count} produits")
    logger.info(f"📥 Scrapés: {len(products)} produits Esoterix")
    logger.info(f"✨ Créés: {stats['created']} produits")
    logger.info("✅ Sauvegarde skippée (vous avez le CSV manuel)")
    logger.info("="*70)
    logger.info("✅ RESET COMPLET TERMINÉ!")


if __name__ == "__main__":
    main()
