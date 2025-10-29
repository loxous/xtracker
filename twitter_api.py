import requests
from config import TWITTER_API_KEY, TWITTER_API_BASE_URL, ENDPOINTS

class TwitterAPI:
    def __init__(self):
        self.api_key = TWITTER_API_KEY
        self.base_url = TWITTER_API_BASE_URL
        self.headers = {
            'X-API-Key': self.api_key
        }
    
    def get_user_info(self, username):
        """Get user information"""
        url = f"{self.base_url}{ENDPOINTS['user_info']}"
        params = {'userName': username}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'success': True,
                    'data': data.get('data')
                }
            else:
                return {
                    'success': False,
                    'error': data.get('msg', 'Unknown error')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_following(self, username, page_size=20, cursor=None):
        """Get user following list"""
        url = f"{self.base_url}{ENDPOINTS['user_following']}"
        params = {
            'userName': username,
            'pageSize': page_size
        }
        
        if cursor:
            params['cursor'] = cursor
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'success': True,
                    'followings': data.get('followings', []),
                    'has_next_page': data.get('has_next_page', False),
                    'next_cursor': data.get('next_cursor')
                }
            else:
                return {
                    'success': False,
                    'error': data.get('msg', 'Unknown error')
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_my_credits(self):
        """Get account credits information"""
        url = f"{self.base_url}{ENDPOINTS['my_info']}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'recharge_credits': data.get('recharge_credits', 0),
                'total_bonus_credits': data.get('total_bonus_credits', 0)
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_new_followings(self, username, difference):
        """Fetch new followings based on difference with pagination support"""
        all_followings = []
        remaining = difference
        cursor = None
        page_count = 0
        max_pages = 10  # Safety limit to prevent infinite loops
        
        while remaining > 0 and page_count < max_pages:
            # Calculate page size for this iteration: min 20, max 200
            page_size = max(20, min(remaining, 200))
            
            # Fetch followings
            result = self.get_user_following(username, page_size=page_size, cursor=cursor)
            
            if not result['success']:
                # If error on first page, return error
                if page_count == 0:
                    return result
                # If error on subsequent pages, return what we have
                break
            
            # Add followings to collection
            followings = result['followings']
            all_followings.extend(followings)
            
            # Update remaining count
            remaining -= len(followings)
            page_count += 1
            
            # Check if we need to continue
            if remaining <= 0:
                break
            
            # Check if there's next page
            if not result.get('has_next_page'):
                break
            
            # Get cursor for next page
            cursor = result.get('next_cursor')
            if not cursor:
                break
        
        # Return only the exact number requested
        new_followings = all_followings[:difference]
        
        return {
            'success': True,
            'new_followings': new_followings,
            'count': len(new_followings),
            'total_fetched': len(all_followings),
            'pages_fetched': page_count
        }