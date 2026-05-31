"""
Network Graph Service
Processes OSINT investigation results into graph data structure.
"""
from typing import Any, Dict, List, Optional
import re


class NetworkGraphService:
    """Generate network graph data from investigation results."""

    TOOL_ENTITY_RULES = {
        'whois': {
            'emails': 'email',
            'nameservers': 'domain',
            'registrar': 'organization'
        },
        'domain-info': {
            'emails': 'email',
            'nameservers': 'domain',
            'registrar': 'organization'
        },
        'ip-checker': {
            'hostname': 'domain',
            'isp': 'organization'
        },
        'ip-lookup': {
            'hostname': 'domain',
            'isp': 'organization'
        },
        'email-breach': {
            'breaches': 'breach'
        },
        'email-osint': {
            'breaches': 'breach'
        },
        'username-search': {
            'platforms': 'platform'
        }
    }

    GENERIC_FIELDS = {
        'domain': 'domain',
        'ip': 'ip',
        'email': 'email',
        'username': 'username',
        'url': 'url',
        'hostname': 'domain',
        'host': 'domain'
    }

    @staticmethod
    def generate_graph_data(investigation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert investigation results into a D3.js-compatible graph structure.

        Args:
            investigation_results: List of investigation result dictionaries.

        Returns:
            Dictionary with 'nodes', 'links', and summary stats.
        """
        nodes: List[Dict[str, Any]] = []
        links: List[Dict[str, Any]] = []
        node_map: Dict[str, str] = {}
        link_pairs = set()
        node_id_counter = 0

        for result in investigation_results or []:
            tool_name = str(result.get('tool_name') or 'unknown').strip() or 'unknown'
            target = NetworkGraphService._stringify_value(result.get('target'))
            result_data = result.get('result_data') if isinstance(result.get('result_data'), dict) else {}
            threat_level = str(result.get('threat_level') or 'low').strip().lower() or 'low'

            entities = NetworkGraphService._extract_entities(target, result_data, tool_name)

            if not entities:
                continue

            for entity in entities:
                entity_key = entity['key']

                if entity_key in node_map:
                    continue

                node_id = f"node_{node_id_counter}"
                node_id_counter += 1
                node_map[entity_key] = node_id

                nodes.append({
                    'id': node_id,
                    'label': entity['value'],
                    'type': entity['type'],
                    'threat_level': threat_level,
                    'tool': tool_name,
                    'size': NetworkGraphService._get_node_size(entity['type'])
                })

            # Connect the primary target to related entities for this result.
            if len(entities) > 1:
                primary_key = entities[0]['key']
                primary_id = node_map.get(primary_key)

                for entity in entities[1:]:
                    target_id = node_map.get(entity['key'])

                    if not primary_id or not target_id or primary_id == target_id:
                        continue

                    pair = tuple(sorted((primary_id, target_id)))
                    if pair in link_pairs:
                        continue

                    link_pairs.add(pair)
                    links.append({
                        'source': primary_id,
                        'target': target_id,
                        'type': 'discovered_via',
                        'tool': tool_name
                    })

        return {
            'nodes': nodes,
            'links': links,
            'stats': {
                'total_nodes': len(nodes),
                'total_links': len(links),
                'node_types': NetworkGraphService._count_node_types(nodes)
            }
        }

    @staticmethod
    def _extract_entities(target: str, result_data: Dict[str, Any], tool_name: str) -> List[Dict[str, str]]:
        """
        Extract entities from the target and tool result data.

        Returns:
            List of dictionaries with normalized entity metadata.
        """
        entities: List[Dict[str, str]] = []

        if target:
            entities.append(NetworkGraphService._build_entity(target))

        tool_rules = NetworkGraphService.TOOL_ENTITY_RULES.get(tool_name, {})

        for field_name, entity_type in tool_rules.items():
            value = result_data.get(field_name)
            if value is None:
                continue

            if field_name == 'breaches' and isinstance(value, list):
                for breach in value[:5]:
                    if isinstance(breach, dict):
                        breach_name = NetworkGraphService._stringify_value(
                            breach.get('Name') or breach.get('name')
                        )
                        if breach_name:
                            entities.append(NetworkGraphService._build_entity(breach_name, entity_type))
                continue

            if field_name == 'platforms' and isinstance(value, list):
                for platform in value[:5]:
                    platform_name = NetworkGraphService._stringify_value(platform)
                    if platform_name:
                        entities.append(NetworkGraphService._build_entity(platform_name, entity_type))
                continue

            if isinstance(value, list):
                for item in value:
                    item_value = NetworkGraphService._stringify_value(item)
                    if item_value:
                        entities.append(NetworkGraphService._build_entity(item_value, entity_type))
            else:
                item_value = NetworkGraphService._stringify_value(value)
                if item_value:
                    entities.append(NetworkGraphService._build_entity(item_value, entity_type))

        for field_name, entity_type in NetworkGraphService.GENERIC_FIELDS.items():
            value = result_data.get(field_name)
            if value is None:
                continue

            if isinstance(value, list):
                for item in value:
                    item_value = NetworkGraphService._stringify_value(item)
                    if item_value:
                        entities.append(NetworkGraphService._build_entity(item_value, entity_type))
                continue

            item_value = NetworkGraphService._stringify_value(value)
            if item_value:
                entities.append(NetworkGraphService._build_entity(item_value, entity_type))

        deduplicated: List[Dict[str, str]] = []
        seen = set()

        for entity in entities:
            if not entity['value'] or entity['key'] in seen:
                continue
            seen.add(entity['key'])
            deduplicated.append(entity)

        return deduplicated

    @staticmethod
    def _build_entity(value: str, entity_type: Optional[str] = None) -> Dict[str, str]:
        """Normalize an entity into a consistent graph node payload."""
        clean_value = NetworkGraphService._normalize_value(value)
        detected_type = entity_type or NetworkGraphService._detect_entity_type(clean_value)
        return {
            'key': clean_value.lower(),
            'value': clean_value,
            'type': detected_type
        }

    @staticmethod
    def _normalize_value(value: str) -> str:
        """Normalize whitespace and trim punctuation around entity values."""
        return re.sub(r'\s+', ' ', str(value or '')).strip().strip(',;')

    @staticmethod
    def _stringify_value(value: Any) -> str:
        """Safely convert a result value into displayable text."""
        if value is None:
            return ''
        if isinstance(value, (str, int, float, bool)):
            return NetworkGraphService._normalize_value(str(value))
        return ''

    @staticmethod
    def _detect_entity_type(value: str) -> str:
        """Detect entity type from a value."""
        if not value:
            return 'other'
        if re.match(r'^\d{1,3}(?:\.\d{1,3}){3}$', value):
            return 'ip'
        if value.startswith(('http://', 'https://')):
            return 'url'
        if '@' in value and re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', value):
            return 'email'
        if '.' in value and ' ' not in value and not value.startswith('@'):
            return 'domain'
        if re.match(r'^[a-zA-Z0-9_.-]+$', value):
            return 'username'
        return 'other'

    @staticmethod
    def _get_node_size(entity_type: str) -> int:
        """Get node size based on entity type."""
        size_map = {
            'ip': 15,
            'domain': 12,
            'email': 10,
            'username': 8,
            'url': 10,
            'organization': 14,
            'breach': 8,
            'platform': 8,
            'other': 6
        }
        return size_map.get(entity_type, 8)

    @staticmethod
    def _count_node_types(nodes: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count nodes by type."""
        counts: Dict[str, int] = {}
        for node in nodes:
            node_type = node.get('type', 'other')
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts
