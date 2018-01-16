from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting


class DamInventory(TethysAppBase):
    """
    Tethys app class for Dam Inventory.
    """

    name = 'Ryan Drought Test'
    index = 'dam_inventory:home'
    icon = 'dam_inventory/images/drought_logo.png'
    package = 'dam_inventory'
    root_url = 'dam-inventory'
    color = '#01AEBF'
    description = 'Ryan testing drought monitoring tool'
    tags = ''
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='dam-inventory',
                controller='dam_inventory.controllers.home'
            ),
            UrlMap(
                name='drought',
                url='dam-inventory/drought',
                controller='dam_inventory.controllers.drought_map'
            ),   
            UrlMap(
                name='drought_fx',
                url='dam-inventory/drought_fx',
                controller='dam_inventory.controllers.drought_map_forecast'
            ),   
            UrlMap(
                name='drought_index',
                url='dam-inventory/drought_index',
                controller='dam_inventory.controllers.drought_index_map'
            ),   
            UrlMap(
                name='drought_prec',
                url='dam-inventory/drought_prec',
                controller='dam_inventory.controllers.drought_prec_map'
            ),   
            UrlMap(
                name='add_dam',
                url='dam-inventory/dams/add',
                controller='dam_inventory.controllers.add_dam'
            ),
            UrlMap(
                name='dams',
                url='dam-inventory/dams',
                controller='dam_inventory.controllers.list_dams'
            ),
        )

        return url_maps

    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting(
                name='max_dams',
                type=CustomSetting.TYPE_INTEGER,
                description='Maximum number of dams that can be created in the app.',
                required=False
            ),
        )
        return custom_settings
