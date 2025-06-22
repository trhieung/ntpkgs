
from typing import List, Optional
from ntproxy.base.public.models import ProxyModel

class NTProxy:
    def __init__(self):
        self.proxies:List[Optional[ProxyModel]] = []

    def add(self, proxy: ProxyModel):
        """
        Add a new proxy configuration to the list.

        Args:
            proxy (ProxyModel): The proxy instance to be added.
        """
        self.proxies.append(proxy)

    def get(self) -> List[Optional[ProxyModel]]:
        """
        Retrieve the list of added proxy configurations.

        Returns:
            List[Optional[ProxyModel]]: The list of proxies added to the container.
        """
        return self.proxies