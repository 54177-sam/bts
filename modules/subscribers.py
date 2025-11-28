from flask import Blueprint, render_template, request, jsonify
from modules.helpers import login_required
from modules.database import get_subscribers as db_get_subscribers, get_subscribers_count as db_get_subscribers_count
from modules.cache import cache_with_timeout, CacheManager
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
subscribers_bp = Blueprint('subscribers', __name__)


class SubscriberManager:
    """Optimized subscriber operations with caching and pagination."""
    
    @staticmethod
    @cache_with_timeout(CacheManager.TIMEOUT_SUBSCRIBERS)
    def get_subscribers(limit=100, offset=0):
        """Get subscribers with pagination and caching."""
        try:
            return db_get_subscribers(limit=limit, offset=offset)
        except Exception as e:
            logger.exception("Error fetching subscribers")
            return []
    
    @staticmethod
    @cache_with_timeout(CacheManager.TIMEOUT_SUBSCRIBERS)
    def get_subscribers_count():
        """Get total subscriber count with caching."""
        try:
            return db_get_subscribers_count()
        except Exception as e:
            logger.exception("Error getting subscriber count")
            return 0
    
    @staticmethod
    def get_subscriber_stats():
        """Get subscriber statistics."""
        try:
            count = SubscriberManager.get_subscribers_count()
            return {
                'total_subscribers': count,
                'active_subscribers': count,  # Simulated
                'inactive_subscribers': 0,
                'last_sync': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception:
            logger.exception("Error getting subscriber stats")
            return {
                'total_subscribers': 0,
                'active_subscribers': 0,
                'inactive_subscribers': 0,
                'last_sync': 'Unknown'
            }


@subscribers_bp.route('/subscribers', methods=['GET'])
@login_required
def subscribers():
    """Subscribers list view with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = (page - 1) * limit
        
        subscriber_manager = SubscriberManager()
        subscribers_list = subscriber_manager.get_subscribers(limit=limit, offset=offset)
        total_count = subscriber_manager.get_subscribers_count()
        stats = subscriber_manager.get_subscriber_stats()
        
        return render_template('subscribers.html',
                             subscribers=subscribers_list,
                             total_count=total_count,
                             page=page,
                             limit=limit,
                             stats=stats,
                             company='SIBERINDO')
    except Exception as e:
        logger.exception("Error loading subscribers")
        return render_template('error.html',
                             error_message=f'Error loading subscribers: {str(e)}',
                             company='SIBERINDO'), 500


@subscribers_bp.route('/api/subscribers', methods=['GET'])
@login_required
def api_subscribers():
    """API endpoint for subscriber list with pagination."""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 100, type=int)
        offset = (page - 1) * limit
        
        subscriber_manager = SubscriberManager()
        subscribers_list = subscriber_manager.get_subscribers(limit=limit, offset=offset)
        total_count = subscriber_manager.get_subscribers_count()
        
        return jsonify({
            'success': True,
            'subscribers': [dict(sub) if hasattr(sub, 'keys') else sub for sub in subscribers_list],
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error in API subscribers")
        return jsonify({'success': False, 'message': str(e)}), 500


@subscribers_bp.route('/api/subscribers/stats', methods=['GET'])
@login_required
def api_subscriber_stats():
    """API endpoint for subscriber statistics."""
    try:
        subscriber_manager = SubscriberManager()
        stats = subscriber_manager.get_subscriber_stats()
        
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error in API subscriber stats")
        return jsonify({'success': False, 'message': str(e)}), 500


@subscribers_bp.route('/api/subscribers/count', methods=['GET'])
@login_required
def api_subscriber_count():
    """API endpoint for getting subscriber count."""
    try:
        subscriber_manager = SubscriberManager()
        count = subscriber_manager.get_subscribers_count()
        
        return jsonify({
            'success': True,
            'count': count,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        logger.exception("Error in API subscriber count")
        return jsonify({'success': False, 'message': str(e)}), 500