import json
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Tuple, Callable
from aiohttp import ClientSession
import certifi
import ssl

# Modul darajasida SSL kontekstini yaratamiz
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


class InstagramAPI:
    def __init__(self, api_key: str, api_host: str = "instagram-social-api.p.rapidapi.com", session_pool_size: int = 5):
        self.api_key = api_key
        self.api_host = api_host
        self.base_url = f"https://{api_host}"
        self.headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': api_host
        }
        # Session pool setup
        self.session_pool_size = session_pool_size
        self._session = None
        self._rate_limit_retry_count = 3
        self._connection_timeout = aiohttp.ClientTimeout(total=30, connect=15)

    async def _get_session(self) -> ClientSession:
        """Get or create session pool for connection reuse"""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.session_pool_size,
                force_close=False,
                ssl=ssl.create_default_context(cafile=certifi.where())  # SSL qo‘shish
            )
            self._session = aiohttp.ClientSession(connector=connector, timeout=self._connection_timeout)
        return self._session




    async def close(self):
        """Close session on shutdown"""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    # ---------- Utility ----------
    @staticmethod
    def _extract_shortcode_from_url(url: str) -> str:
        print("Extracting shortcode from URL:", url)
        """
        Extract shortcode from common Instagram URL forms:
        - https://www.instagram.com/p/DQgR3A5DfoK/
        - https://instagram.com/reel/DQgR3A5DfoK
        - https://instagram.com/p/DQgR3A5DfoK/?utm_source=...
        - Or if already shortcode, return it unchanged.
        """
        if not url:
            return ""
        u = url.strip()
        # remove query and fragment
        if "?" in u:
            u = u.split("?", 1)[0]
        if "#" in u:
            u = u.split("#", 1)[0]
        # strip trailing slash
        if u.endswith("/"):
            u = u[:-1]
        parts = u.split("/")
        # If URL contains instagram domain, find segments p/reel/reels
        if "instagram.com" in u:
            for i, part in enumerate(parts):
                if part in ("p", "reel", "reels"):
                    if i + 1 < len(parts):
                        return parts[i + 1]
            # fallback: last part (if url ends with shortcode)
            return parts[-1] if parts else ""
        # if input looked like a shortcode already
        return u

    # ---------- User / followers ----------
    async def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram user info using Instagram Social API
        """
        url = f"{self.base_url}/v1/info"
        params = {"username_or_id_or_url": username}

        session = await self._get_session()
        try:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Accept several possible structures
                    user = None
                    if isinstance(data, dict):
                        if "data" in data:
                            user = data["data"]
                        elif "user" in data:
                            user = data["user"]
                        else:
                            user = data
                    if user:
                        return {
                            "id": str(user.get("id", "")),
                            "username": user.get("username", username),
                            "full_name": user.get("full_name", ""),
                            "followers_count": user.get("follower_count", user.get("followers_count", 0)),
                            "following_count": user.get("following_count", 0),
                            "posts_count": user.get("media_count", user.get("posts_count", 0)),
                            "bio": user.get("biography", ""),
                            "is_verified": user.get("is_verified", False),
                            "is_private": user.get("is_private", False),
                            "profile_pic_url": user.get("profile_pic_url", user.get("profile_pic_url_hd", "")),
                            "external_url": user.get("external_url", "")
                        }
                    else:
                        print(f"API response error (user info): {data}")
                        return None
                elif response.status == 404:
                    print(f"User {username} not found")
                    return None
                else:
                    error_text = await response.text()
                    print(f"API error (user info): {response.status} - {error_text}")
                    return None

        except asyncio.TimeoutError:
            print(f"Timeout error for user {username}")
            return None
        except Exception as e:
            print(f"Unexpected error getting user info for {username}: {e}")
            return None

    async def get_user_followers(self, username_or_id: str, count: int = 50) -> List[Dict[str, str]]:
        """
        Get user followers using Instagram Social API
        """
        url = f"{self.base_url}/v1/followers"
        params = {"username_or_id_or_url": username_or_id, "count": count}

        session = await self._get_session()
        try:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    followers = []

                    items = None
                    if isinstance(data, dict):
                        items = data.get("data", {}).get("items") or data.get("items") or data.get("data")
                    if items and isinstance(items, list):
                        for user in items:
                            if user.get("username"):
                                followers.append({
                                    "username": user.get("username", ""),
                                    "id": str(user.get("id", "")),
                                    "full_name": user.get("full_name", ""),
                                    "link": f"https://www.instagram.com/{user.get('username', '')}",
                                    "is_verified": user.get("is_verified", False),
                                    "is_private": user.get("is_private", False),
                                    "profile_pic_url": user.get("profile_pic_url", "")
                                })

                    return followers
                else:
                    error_text = await response.text()
                    print(f"API error getting followers: {response.status} - {error_text}")
                    return []

        except Exception as e:
            print(f"Error getting followers: {e}")
            return []

    # (the batch / multiple batches / all_followers_with_progress remain unchanged except they use above batch call)
    async def get_user_followers_batch(self, username_or_id: str, count: int = 100, pagination_token: str = None) -> Dict[str, Any]:
        """
        Get a batch of followers with pagination support
        """
        url = f"{self.base_url}/v1/followers"
        params = {"username_or_id_or_url": username_or_id, "count": count}
        if pagination_token:
            params["pagination_token"] = pagination_token

        session = await self._get_session()

        for attempt in range(self._rate_limit_retry_count + 1):
            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("data", {}).get("items") or data.get("items") or data.get("data")
                        followers = []
                        if items and isinstance(items, list):
                            for user in items:
                                if user.get("username"):
                                    followers.append({
                                        "username": user.get("username", ""),
                                        "id": str(user.get("id", "")),
                                        "full_name": user.get("full_name", ""),
                                        "link": f"https://www.instagram.com/{user.get('username', '')}",
                                        "is_verified": user.get("is_verified", False),
                                        "is_private": user.get("is_private", False),
                                        "profile_pic_url": user.get("profile_pic_url", "")
                                    })
                        # try to find next token in common places
                        next_pagination_token = data.get("pagination_token") or data.get("data", {}).get("pagination_token") or data.get("next_max_id") or data.get("data", {}).get("next_max_id")
                        return {
                            "followers": followers,
                            "next_max_id": next_pagination_token,
                            "has_more": bool(next_pagination_token),
                            "count": len(followers)
                        }

                    elif response.status == 429:
                        if attempt < self._rate_limit_retry_count:
                            backoff_time = 2 ** attempt
                            print(f"Rate limit exceeded. Retrying in {backoff_time} seconds...")
                            await asyncio.sleep(backoff_time)
                            continue
                        else:
                            print(f"Rate limit exceeded after {attempt + 1} attempts")
                            return {"followers": [], "next_max_id": None, "has_more": False, "count": 0}

                    elif response.status == 404:
                        print(f"User {username_or_id} not found")
                        return {"followers": [], "next_max_id": None, "has_more": False, "count": 0}
                    else:
                        error_text = await response.text()
                        print(f"API error: {response.status} - {error_text}")
                        if attempt < self._rate_limit_retry_count:
                            await asyncio.sleep(2)
                            continue
                        return {"followers": [], "next_max_id": None, "has_more": False, "count": 0}

            except asyncio.TimeoutError:
                print(f"Timeout error (attempt {attempt + 1}/{self._rate_limit_retry_count + 1})")
                if attempt < self._rate_limit_retry_count:
                    await asyncio.sleep(2)
                    continue
                return {"followers": [], "next_max_id": None, "has_more": False, "count": 0}
            except Exception as e:
                print(f"Unexpected error fetching followers: {e}")
                if attempt < self._rate_limit_retry_count:
                    await asyncio.sleep(2)
                    continue
                return {"followers": [], "next_max_id": None, "has_more": False, "count": 0}

        return {"followers": [], "next_max_id": None, "has_more": False, "count": 0}

    async def get_multiple_batches(self, username_or_id: str, count: int, pagination_tokens: List[str]) -> List[Dict[str, Any]]:
        if not pagination_tokens:
            return []
        tasks = [
            self.get_user_followers_batch(username_or_id, count, pagination_token)
            for pagination_token in pagination_tokens
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = []
        for result in results:
            if not isinstance(result, Exception) and result.get('followers'):
                valid_results.append(result)
            elif isinstance(result, Exception):
                print(f"Exception in batch request: {result}")
        return valid_results

    async def get_all_followers_with_progress(
            self,
            username_or_id: str,
            progress_callback: Optional[Callable] = None,
            max_followers: Optional[int] = None
    ) -> List[Dict[str, str]]:
        all_followers = []
        pagination_token = None
        batch_count = 0

        while True:
            batch_count += 1
            if progress_callback:
                try:
                    await progress_callback(len(all_followers), max_followers, batch_count)
                except Exception as e:
                    print(f"Error in progress callback: {e}")

            batch_result = await self.get_user_followers_batch(
                username_or_id=username_or_id,
                count=50,
                pagination_token=pagination_token
            )

            if not batch_result or not batch_result.get('followers'):
                print(f"No more followers found after {batch_count} batches")
                break

            new_followers = batch_result.get('followers', [])
            if max_followers:
                remaining_slots = max_followers - len(all_followers)
                if remaining_slots <= 0:
                    break
                if len(new_followers) > remaining_slots:
                    new_followers = new_followers[:remaining_slots]

            all_followers.extend(new_followers)
            if max_followers and len(all_followers) >= max_followers:
                print(f"Reached follower limit of {max_followers}")
                break

            pagination_token = batch_result.get('next_max_id')
            if not pagination_token or not batch_result.get('has_more', False):
                print(f"Reached end of followers list after {batch_count} batches")
                break

            await asyncio.sleep(0.5)
            if batch_count > 2000:
                print(f"Reached safety limit of {batch_count} batches")
                break

        print(f"Total followers fetched: {len(all_followers)} in {batch_count} batches")
        return all_followers

    # ---------- Following ----------
    async def get_user_following(self, username_or_id: str) -> List[Dict[str, str]]:
        url = f"{self.base_url}/v1/following"
        params = {"username_or_id_or_url": username_or_id}
        session = await self._get_session()
        try:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("data", {}).get("items") or data.get("items") or data.get("data")
                    following = []
                    if items and isinstance(items, list):
                        for user in items:
                            if user.get("username"):
                                following.append({
                                    "username": user.get("username", ""),
                                    "id": str(user.get("id", "")),
                                    "full_name": user.get("full_name", ""),
                                    "link": f"https://www.instagram.com/{user.get('username', '')}",
                                    "is_verified": user.get("is_verified", False),
                                    "is_private": user.get("is_private", False)
                                })
                    return following
                else:
                    print(f"Following endpoint may not be available: {response.status}")
                    return []
        except Exception as e:
            print(f"Error getting following list: {e}")
            return []

    async def health_check(self) -> bool:
        try:
            test_result = await self.get_user_info("instagram")
            return test_result is not None
        except Exception as e:
            print(f"Health check failed: {e}")
            return False

    # ---------- Posts & Comments ----------
    async def get_post_comments(self, post_url_or_id: str, max_comments: Optional[int] = None) -> List[Dict[str, Any]]:
        print("Fetching comments for post:", post_url_or_id)
        """
        Get comments for a post. Uses RapidAPI param name `code_or_id_or_url`.
        """
        url = f"{self.base_url}/v1/comments"

        # Extract shortcode if a full URL provided
        shortcode = post_url_or_id
        if isinstance(post_url_or_id, str) and "instagram.com" in post_url_or_id:
            shortcode = self._extract_shortcode_from_url(post_url_or_id)

        params = {"code_or_id_or_url": shortcode}
        # if caller requested max_comments, attempt to pass as count/limit (API may accept one of them)
        if max_comments is not None:
            try:
                c = int(max_comments)
                if c > 0:
                    params["count"] = c
            except Exception:
                pass

        all_comments: List[Dict[str, Any]] = []
        pagination_token = None
        session = await self._get_session()

        while True:
            if pagination_token:
                params["pagination_token"] = pagination_token

            try:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Try multiple locations for items
                        items = None
                        if isinstance(data, dict):
                            items = data.get("data", {}).get("items") or data.get("items") or data.get("data")
                        if items and isinstance(items, list):
                            for comment in items:
                                user_obj = comment.get("user", {}) if isinstance(comment, dict) else {}
                                comment_data = {
                                    "id": str(comment.get("id", "")) if isinstance(comment, dict) else "",
                                    "text": comment.get("text", "") if isinstance(comment, dict) else str(comment),
                                    "username": user_obj.get("username", "") if isinstance(user_obj, dict) else "",
                                    "user_id": str(user_obj.get("id", "")) if isinstance(user_obj, dict) else "",
                                    "full_name": user_obj.get("full_name", "") if isinstance(user_obj, dict) else "",
                                    "profile_pic_url": user_obj.get("profile_pic_url", "") if isinstance(user_obj, dict) else "",
                                    "is_verified": user_obj.get("is_verified", False) if isinstance(user_obj, dict) else False,
                                    "like_count": comment.get("like_count", 0) if isinstance(comment, dict) else 0,
                                    "created_at": comment.get("created_at", 0) if isinstance(comment, dict) else 0,
                                    "has_liked": comment.get("has_liked", False) if isinstance(comment, dict) else False
                                }
                                all_comments.append(comment_data)

                                # respect max_comments limit if provided
                                if max_comments and len(all_comments) >= max_comments:
                                    return all_comments[:max_comments]

                            # pagination token fallback locations
                            pagination_token = data.get("pagination_token") or data.get("data", {}).get("pagination_token") or data.get("next_max_id") or data.get("data", {}).get("next_max_id")
                            if not pagination_token:
                                break

                            await asyncio.sleep(0.5)
                        else:
                            # If items not found but data contains comments as dict/list directly
                            if isinstance(data, list):
                                # treat it as comments list
                                for comment in data:
                                    all_comments.append(comment)
                                break
                            # nothing else to process
                            break
                    else:
                        error_text = await response.text()
                        print(f"API error getting comments: {response.status} - {error_text}")
                        break

            except asyncio.TimeoutError:
                print("Timeout while fetching comments")
                break
            except Exception as e:
                print(f"Error getting comments: {e}")
                break

        return all_comments

    async def get_post_info(self, post_url_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram post information. Uses RapidAPI param name `code_or_id_or_url`.
        """
        url = f"{self.base_url}/v1/post"

        shortcode = post_url_or_id
        if isinstance(post_url_or_id, str) and "instagram.com" in post_url_or_id:
            shortcode = self._extract_shortcode_from_url(post_url_or_id)

        params = {"code_or_id_or_url": shortcode}

        session = await self._get_session()
        try:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # many APIs wrap result in data or post
                    post = None
                    if isinstance(data, dict):
                        post = data.get("data") or data.get("post") or data
                    if post:
                        return {
                            "id": str(post.get("id", "")),
                            "shortcode": post.get("shortcode", shortcode),
                            "caption": (post.get("caption", {}) or {}).get("text", "") if isinstance(post.get("caption", {}), dict) else post.get("caption", ""),
                            "like_count": post.get("like_count", 0),
                            "comment_count": post.get("comment_count", 0),
                            "owner_username": (post.get("owner", {}) or {}).get("username", "") if isinstance(post.get("owner", {}), dict) else "",
                            "owner_full_name": (post.get("owner", {}) or {}).get("full_name", "") if isinstance(post.get("owner", {}), dict) else "",
                            "is_video": post.get("is_video", False),
                            "video_view_count": post.get("video_view_count", 0) if post.get("is_video") else 0,
                            "created_at": post.get("taken_at_timestamp", post.get("created_at", 0)),
                            "url": f"https://www.instagram.com/p/{post.get('shortcode', shortcode)}"
                        }
                    else:
                        print(f"API response error (post info): {data}")
                        return None
                else:
                    error_text = await response.text()
                    print(f"API error (post info): {response.status} - {error_text}")
                    return None
        except Exception as e:
            print(f"Error getting post info: {e}")
            return None

    def get_api_info(self) -> Dict[str, str]:
        """
        Get information about the current API configuration
        """
        return {
            "api_host": self.api_host,
            "base_url": self.base_url,
            "has_api_key": bool(self.api_key),
            "session_pool_size": self.session_pool_size,
            "retry_count": self._rate_limit_retry_count
        }
        