from pytz import utc

import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401
from CommonServerUserPython import *  # noqa

''' CONSTANTS '''

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'  # ISO8601 format with UTC, default in XSOAR

HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

# In the documentation, the state 'all' is written as 'ALL'. As the latter doesn't work, we use 'all''.
ALERT_STATES = {'all', 'no_data', 'paused', 'alerting', 'ok', 'pending'}

MAX_INCIDENTS_TO_FETCH = 50

FETCH_DEFAULT_TIME = '3 days'

''' CLIENT CLASS '''


class Client(BaseClient):
    def __init__(self, server_url, verify=True, proxy=False, headers=None, auth=None):
        super().__init__(base_url=server_url, verify=verify, proxy=proxy, headers=headers, auth=auth)

    def alerts_list_request(self, dashboard_id: Optional[List[str]] = None, panel_id: str = None, query: str = None,
                            state: List[str] = None, limit: str = None, folder_id: List[str] = None,
                            dashboard_query: str = None, dashboard_tag: List[str] = None):
        # query works this way- we can get it with parenthesis or without, it adds to it
        params = assign_params(dashboardId=dashboard_id, panelId=panel_id, query=query, state=state, limit=limit,
                               folderId=folder_id, dashboardQuery=dashboard_query, dashboardTag=dashboard_tag)
        response = self._http_request('GET', 'api/alerts', params=params, headers=self._headers)
        response = self._concatenate_url(response)
        return response

    def alert_pause_request(self, alert_id: str, paused: bool):
        data = {"paused": paused}

        response = self._http_request('POST', f'api/alerts/{alert_id}/pause', json_data=data, headers=self._headers)

        return response

    def alert_get_by_id_request(self, alert_id: str):
        response = self._http_request('GET', f'api/alerts/{alert_id}', headers=self._headers)

        return response

    def users_search_request(self, perpage: str = None, page: str = None, query: str = None):
        params = assign_params(perpage=perpage, page=page, query=query)

        response = self._http_request('GET', 'api/users', params=params, headers=self._headers)

        return response

    def user_get_by_id_request(self, user_id: str):
        response = self._http_request('GET', f'api/users/{user_id}', headers=self._headers)

        return response

    def users_teams_request(self, user_id: str):
        response = self._http_request('GET', f'api/users/{user_id}/teams', headers=self._headers)

        return response

    def users_organization_request(self, user_id: str):
        response = self._http_request('GET', f'api/users/{user_id}/orgs', headers=self._headers)

        return response

    def user_update_request(self, user_id: str, email: str = None, name: str = None, login: str = None,
                            theme: str = None):
        data = {"email": email, "login": login, "name": name, "theme": theme}

        response = self._http_request('PUT', f'api/users/{user_id}', json_data=data, headers=self._headers)

        return response

    def annotation_create_request(self, text: str, dashboard_id: str = None, panel_id: str = None,
                                  time_start: str = None, time_end: str = None, tags: List[str] = None):
        data = {"dashboardId": dashboard_id, "panelId": panel_id,
                "tags": tags, "text": text, "time": time_start, "timeEnd": time_end}

        response = self._http_request('POST', 'api/annotations', json_data=data, headers=self._headers)

        return response

    def teams_search_request(self, perpage: str = None, page: str = None, query: str = None, name: str = None):
        params = assign_params(perpage=perpage, page=page, query=query, name=name)

        response = self._http_request('GET', 'api/teams/search', params=params, headers=self._headers)

        return response

    def team_get_by_id_request(self, team_id: str):
        response = self._http_request('GET', f'api/teams/{team_id}', headers=self._headers)

        return response

    def team_members_request(self, team_id: str):
        response = self._http_request('GET', f'api/teams/{team_id}/members', headers=self._headers)

        return response

    def user_add_to_team_request(self, team_id: str, user_id: str):
        data = {"userId": int(user_id)}

        # 400 - 'User is already added to this team' might be raised - which isn't a real error
        response = self._http_request('POST', f'api/teams/{team_id}/members', json_data=data, headers=self._headers,
                                      ok_codes=(200, 400))

        return response

    def user_remove_from_team_request(self, team_id: str, user_id: str):
        response = self._http_request('DELETE', f'api/teams/{team_id}/members/{user_id}', headers=self._headers)

        return response

    def team_add_request(self, name: str, email: str = None, org_id: str = None):
        data = {"email": email, "name": name, "orgId": org_id}

        response = self._http_request('POST', 'api/teams', json_data=data, headers=self._headers)

        return response

    def team_delete_request(self, team_id: str):
        response = self._http_request('DELETE', f'api/teams/{team_id}', headers=self._headers)

        return response

    def org_create_request(self, name: str):
        data = {"name": name}

        response = self._http_request('POST', 'api/orgs', json_data=data, headers=self._headers)

        return response

    def org_list_request(self, perpage: str = None, page: str = None):
        params = assign_params(perpage=perpage, page=page)

        response = self._http_request('GET', 'api/orgs', params=params, headers=self._headers)

        return response

    def org_get_by_name_request(self, name: str):
        response = self._http_request('GET', f'api/orgs/name/{name}', headers=self._headers)

        return response

    def org_get_by_id_request(self, org_id: str = None):
        response = self._http_request('GET', f'api/orgs/{org_id}', headers=self._headers)

        return response

    def dashboards_search_request(self, query: str = None, tag: List[str] = None, type_: str = None,
                                  dashboard_ids: List[str] = None, folder_ids: List[str] = None, starred: str = None,
                                  limit: str = None, page: str = None):
        params = assign_params(query=query, tag=tag, type=type_, dashboardIds=dashboard_ids,
                               folderIds=folder_ids, starred=starred, limit=limit, page=page)

        response = self._http_request('GET', 'api/search', params=params, headers=self._headers)
        response = self._concatenate_url(response)

        return response

    def _concatenate_url(self, response: List[Dict[str, Any]]):
        """
        Concatenates a url suffix with the base url, for the places where only a suffix is returned.
        Updates the dict given, and returns it.
        """
        for r in response:
            if 'url' in r:
                url = urljoin(self._base_url, r['url'])
                r['url'] = url
        return response


''' HELPER FUNCTIONS '''


def change_key(response: dict, prev_key: str, new_key: str):
    """
    This function changes a key in response, so the values could be aggregated with other functions.
    """
    if prev_key in response:
        response[new_key] = response.pop(prev_key)
    demisto.debug(f'changing key "{prev_key}" in response to "{new_key}", edited response is: {response}')
    return response


def lower_keys(response: dict):
    """
    Lowers firsts letter of all keys in the dictionary given and returns the new dictionary.
    """
    demisto.debug(f'lowering keys for response: {response}')
    return dict((decapitalize(key), value) for (key, value) in response.items())


def decapitalize(s: str):
    """
    Decapitalizes a given string.
    """
    if not s:
        return s
    demisto.debug(f'de-capitalizing key: {s}')
    return s[0].lower() + s[1:]


def url_encode(query: Optional[str]):
    """
    Query values with spaces need to be URL encoded e.g. query=Jane%20Doe.
    """
    if query:
        demisto.debug(f'url-encoding query {query}')
        return query.replace(' ', '%20')
    return None


def calculate_fetch_start_time(last_fetch: str = None, first_fetch: str = FETCH_DEFAULT_TIME):
    first_fetch_dt = dateparser.parse(first_fetch).replace(tzinfo=utc, microsecond=0)
    if last_fetch is None:
        return first_fetch_dt

    last_fetch = dateparser.parse(last_fetch).replace(tzinfo=utc, microsecond=0)
    return max(last_fetch, first_fetch_dt)


def parse_alerts(alerts: List[Dict[str, Any]], max_fetch: int, last_fetch: datetime):
    incidents: List[Dict[str, Any]] = []
    count = 0
    updated_last_fetch = last_fetch

    # sorting alerts by newStateDate so the fetch will work by date and not by id
    alerts.sort(key=lambda a: dateparser.parse(a['newStateDate']).replace(tzinfo=utc))

    for alert in alerts:
        if count >= max_fetch:
            break
        # ignoring microsecond because date_to_timestamp doesn't know how to handle it
        # which causes the last alert to be fetched every time the function is called
        new_state_date = dateparser.parse(alert['newStateDate']).replace(tzinfo=utc, microsecond=0)
        incident = parse_alert(alert, new_state_date, last_fetch)
        if incident:
            incidents.append(incident)
            count += 1
            if new_state_date > updated_last_fetch:
                updated_last_fetch = new_state_date

    return updated_last_fetch, incidents


def parse_alert(alert: Dict[str, Any], new_state_date: datetime, last_fetch: datetime):
    if last_fetch:
        if new_state_date <= last_fetch:
            return None

    alert['type'] = 'Grafana Alert'
    incident = {
        'name': alert['name'],
        'occurred': alert['newStateDate'],
        'rawJSON': json.dumps(alert),
        'type': 'Grafana Alert'
    }
    return incident


''' COMMAND FUNCTIONS '''


def alerts_list_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    dashboard_id = argToList(args.get('dashboard_id', ''))

    panel_id = args.get('panel_id')
    query = args.get('query')

    state = argToList(args.get('state', ''))
    if state:
        if state not in ALERT_STATES:
            raise DemistoException("State must be of: all, no_data, paused, alerting, ok, pending.")

    limit = args.get('limit')
    folder_id = argToList(args.get('folder_id', ''))
    dashboard_query = args.get('dashboard_query')
    dashboard_tag = argToList(args.get('dashboard_tag', ''))

    response = client.alerts_list_request(dashboard_id, panel_id, query, state,
                                          limit, folder_id, dashboard_query, dashboard_tag)

    command_results = CommandResults(
        outputs_prefix='Grafana.Alert',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Alerts', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def alert_pause_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    alert_id = str(args.get('alert_id'))

    response = client.alert_pause_request(alert_id, True)

    output = change_key(dict(response), 'alertId', 'id')
    output.pop('message', None)

    command_results = CommandResults(
        outputs_prefix='Grafana.Alert',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Paused Alert', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def alert_unpause_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    alert_id = str(args.get('alert_id'))

    response = client.alert_pause_request(alert_id, False)

    output = change_key(dict(response), 'alertId', 'id')
    output.pop('message', None)

    command_results = CommandResults(
        outputs_prefix='Grafana.Alert',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Un-paused Alerts', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def alert_get_by_id_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    alert_id = str(args.get('alert_id'))

    response = client.alert_get_by_id_request(alert_id)
    # output returns keys capitalized rather then with first lower case letter (as stated and should be)
    response = lower_keys(response)

    command_results = CommandResults(
        outputs_prefix='Grafana.Alert',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Alert', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def users_search_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    perpage = args.get('perpage')
    page = args.get('page')
    query = args.get('query')
    query = url_encode(query)

    response = client.users_search_request(perpage, page, query)
    command_results = CommandResults(
        outputs_prefix='Grafana.User',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Users', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def user_get_by_id_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    user_id = str(args.get('user_id'))

    response = client.user_get_by_id_request(user_id)
    command_results = CommandResults(
        outputs_prefix='Grafana.User',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('User', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def users_teams_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    user_id = str(args.get('user_id'))

    response = client.users_teams_request(user_id)
    output = {'id': user_id, 'teams': response}

    command_results = CommandResults(
        outputs_prefix='Grafana.User',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Teams For User', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def users_organization_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    user_id = str(args.get('user_id'))

    response = client.users_organization_request(user_id)
    output = {'id': user_id, 'orgs': response}

    command_results = CommandResults(
        outputs_prefix='Grafana.User',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Organization For User', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def user_update_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    user_id = str(args.get('user_id'))
    email = args.get('email')
    name = args.get('name')
    login = args.get('login')
    theme = args.get('theme')

    # login\email is required
    if not login and not email:
        raise DemistoException("Login or email must be filled.")

    response = client.user_update_request(user_id, email, name, login, theme)
    command_results = CommandResults(
        readable_output=response['message']
    )

    return command_results


def annotation_create_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    dashboard_id = args.get('dashboard_id')
    panel_id = args.get('panel_id')

    #  epoch numbers in millisecond resolution
    time_start = args.get('time')
    if time_start:
        time_start = str(date_to_timestamp(time_start, DATE_FORMAT))
    time_end = args.get('time_end')
    if time_end:
        time_end = str(date_to_timestamp(time_end, DATE_FORMAT))

    tags = argToList(args.get('tags', ''))
    text = str(args.get('text'))

    response = client.annotation_create_request(text, dashboard_id, panel_id, time_start, time_end, tags)
    output = dict(response)
    output.pop('message')

    command_results = CommandResults(
        outputs_prefix='Grafana.Annotation',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Annotation', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def teams_search_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    perpage = args.get('perpage')
    page = args.get('page')
    query = args.get('query')
    query = url_encode(query)
    name = args.get('name')

    response = client.teams_search_request(perpage, page, query, name)

    command_results = CommandResults(
        outputs_prefix='Grafana.Team',
        outputs_key_field='id',
        outputs=response['teams'],
        raw_response=response['teams'],
        readable_output=tableToMarkdown('Teams', response['teams'], removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def team_get_by_id_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    team_id = str(args.get('team_id'))

    response = client.team_get_by_id_request(team_id)
    command_results = CommandResults(
        outputs_prefix='Grafana.Team',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Team', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def team_members_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    team_id = str(args.get('team_id'))

    response = client.team_members_request(team_id)
    output = {'id': team_id, 'members': response}

    command_results = CommandResults(
        outputs_prefix='Grafana.Team',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Team Members', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def user_add_to_team_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    team_id = str(args.get('team_id'))
    user_id = str(args.get('user_id'))

    response = client.user_add_to_team_request(team_id, user_id)
    command_results = CommandResults(
        readable_output=response['message']
    )

    return command_results


def user_remove_from_team_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    team_id = str(args.get('team_id'))
    user_id = str(args.get('user_id'))

    response = client.user_remove_from_team_request(team_id, user_id)
    command_results = CommandResults(
        readable_output=response['message']
    )

    return command_results


def team_add_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    name = str(args.get('name'))
    email = args.get('email')
    org_id = args.get('org_id')

    response = client.team_add_request(name, email, org_id)
    output = change_key(dict(response), 'teamId', 'id')

    command_results = CommandResults(
        outputs_prefix='Grafana.Team',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Added Team', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def team_delete_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    team_id = str(args.get('team_id'))

    response = client.team_delete_request(team_id)
    command_results = CommandResults(
        readable_output=response['message']
    )

    return command_results


def org_create_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    name = str(args.get('name'))

    response = client.org_create_request(name)
    output = change_key(dict(response), 'orgId', 'id')

    command_results = CommandResults(
        outputs_prefix='Grafana.Organization',
        outputs_key_field='id',
        outputs=output,
        raw_response=response,
        readable_output=tableToMarkdown('Added Organization', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def org_list_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    perpage = args.get('perpage')
    page = args.get('page')  # reply doesn't show this and total

    response = client.org_list_request(perpage, page)
    command_results = CommandResults(
        outputs_prefix='Grafana.Organization',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Organization', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def org_get_by_name_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    name = str(args.get('name'))

    response = client.org_get_by_name_request(name)
    command_results = CommandResults(
        outputs_prefix='Grafana.Organization',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Organization', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def org_get_by_id_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    org_id = args.get('org_id')

    response = client.org_get_by_id_request(org_id)
    command_results = CommandResults(
        outputs_prefix='Grafana.Organization',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Organization', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def dashboards_search_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    query = args.get('query')
    tag = argToList(args.get('tag', ''))
    type_ = args.get('type')
    dashboard_ids = argToList(args.get('dashboard_ids', ''))
    folder_ids = argToList(args.get('folder_ids', ''))
    starred = args.get('starred')
    limit = args.get('limit')
    page = args.get('page')

    response = client.dashboards_search_request(query, tag, type_, dashboard_ids, folder_ids, starred, limit, page)
    command_results = CommandResults(
        outputs_prefix='Grafana.Dashboard',
        outputs_key_field='id',
        outputs=response,
        raw_response=response,
        readable_output=tableToMarkdown('Dashboard', response, removeNull=True, headerTransform=pascalToSpace)
    )

    return command_results


def test_module(client: Client) -> None:
    message: str = ''
    try:
        if client.users_search_request():
            message = 'ok'

    except DemistoException as e:
        if 'Forbidden' in str(e) or 'Authorization' in str(e):
            message = 'Authorization Error: make sure username and password are correctly set'
        else:
            raise e
    return return_results(message)


def fetch_incidents(client: Client, first_fetch: str, dashboard_id: str = None, panel_id: str = None,
                    alert_name: str = None, state: str = None, max_fetch: int = MAX_INCIDENTS_TO_FETCH) -> List[dict]:
    last_fetch = demisto.getLastRun().get('last_fetch', None)
    fetch_time = calculate_fetch_start_time(last_fetch, first_fetch)
    demisto.debug(f'last fetch was at: {last_fetch}, time to fetch from is: {fetch_time}')
    alerts = client.alerts_list_request(dashboard_id=argToList(dashboard_id), panel_id=panel_id, query=alert_name,
                                        state=argToList(state))
    last_fetch, incidents = parse_alerts(alerts, max_fetch, fetch_time)
    demisto.debug(f'last fetch now is: {last_fetch}, number of incidents fetched is {len(incidents)}')
    demisto.setLastRun({'last_fetch': str(date_to_timestamp(last_fetch, DATE_FORMAT))})
    return incidents


''' MAIN FUNCTION '''


def main():
    """main function, parses params and runs command functions
    """
    params = demisto.params()
    args = demisto.args()
    url = params.get('url')
    verify_certificate = not params.get('insecure', False)
    proxy = params.get('proxy', False)

    username = params['credentials']['identifier']
    password = params['credentials']['password']
    # we chose to use only Basic authentication, even though in some requests a Bearer authentication is documented
    # and is enough, because for some other queries Basic authentication is required

    command = demisto.command()
    demisto.debug(f'Command being called is {command}')

    try:
        requests.packages.urllib3.disable_warnings()
        client = Client(urljoin(url, ''), verify_certificate, proxy, headers=HEADERS, auth=(username, password))

        commands = {
            'grafana-alerts-list': alerts_list_command,
            'grafana-alert-pause': alert_pause_command,
            'grafana-alert-unpause': alert_unpause_command,
            'grafana-alert-get-by-id': alert_get_by_id_command,
            'grafana-users-search': users_search_command,
            'grafana-user-get-by-id': user_get_by_id_command,
            'grafana-user-teams-get': users_teams_command,
            'grafana-user-orgs-get': users_organization_command,
            'grafana-user-update': user_update_command,
            'grafana-annotation-create': annotation_create_command,
            'grafana-teams-search': teams_search_command,
            'grafana-team-get-by-id': team_get_by_id_command,
            'grafana-team-members-list': team_members_command,
            'grafana-user-add-to-team': user_add_to_team_command,
            'grafana-user-remove-from-team': user_remove_from_team_command,
            'grafana-team-add': team_add_command,
            'grafana-team-delete': team_delete_command,
            'grafana-org-create': org_create_command,
            'grafana-org-list': org_list_command,
            'grafana-org-get-by-name': org_get_by_name_command,
            'grafana-org-get-by-id': org_get_by_id_command,
            'grafana-dashboards-search': dashboards_search_command
        }

        if command == 'fetch-incidents':
            first_fetch = params.get('first_fetch', FETCH_DEFAULT_TIME)

            dashboard_id = params.get('dashboard_id', None)
            panel_id = params.get('panel_id', None)
            alert_name = params.get('alert_name', None)
            state = params.get('state', None)

            max_results = arg_to_number(arg=params.get('max_fetch'), arg_name='max_fetch', required=False)
            if not max_results or max_results > MAX_INCIDENTS_TO_FETCH:
                max_results = MAX_INCIDENTS_TO_FETCH

            incidents = fetch_incidents(client, first_fetch, dashboard_id, panel_id, alert_name, state, max_results)
            demisto.incidents(incidents)

        elif command == 'test-module':
            test_module(client)
        elif command in commands:
            return_results(commands[command](client, args))
        else:
            raise NotImplementedError(f'{command} command is not implemented.')

    except Exception as e:
        return_error(str(e))


''' ENTRY POINT '''

if __name__ in ['__main__', 'builtin', 'builtins']:
    main()
