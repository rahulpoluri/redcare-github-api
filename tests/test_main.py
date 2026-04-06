class TestHealthEndpoint:
    Endpoint = "get_health"

    def test_get_health_return_200(self, client, app_main):
        response = client.get(app_main.url_path_for(self.Endpoint))
        assert response.status_code == 200
        assert response.json() == {"healthy": True}
