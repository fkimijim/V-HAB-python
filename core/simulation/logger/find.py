class Logger:
    def __init__(self):
        """
        Initialize the logger with empty log values and virtual values.
        """
        self.tLogValues = []  # List of dictionaries representing log entries
        self.tVirtualValues = []  # List of dictionaries for virtual log entries

    def find(self, cxItems=None, tFilter=None):
        """
        Find log indexes based on provided items and filters.

        Args:
            cxItems (list): List of integers (indexes) or strings (names/labels).
            tFilter (dict): Dictionary of filter criteria.

        Returns:
            list: List of matching log indexes.

        Raises:
            ValueError: If no matching log items are found.
        """
        # Step 1: Handle empty cxItems (return all indexes)
        if cxItems is None or not cxItems:
            aiIndex = list(range(len(self.tLogValues)))
        else:
            # Step 2: Convert names/labels to indexes
            aiIndex = []
            for item in cxItems:
                if isinstance(item, int):
                    aiIndex.append(item)
                elif isinstance(item, str):
                    # Search for matching names or labels in tLogValues
                    index = next(
                        (i for i, log in enumerate(self.tLogValues) if log.get("sName") == item or log.get("sLabel") == item),
                        None,
                    )
                    if index is None:
                        # Search in tVirtualValues if not found in tLogValues
                        index = next(
                            (-i - 1 for i, log in enumerate(self.tVirtualValues) if log.get("sName") == item or log.get("sLabel") == item),
                            None,
                        )
                    if index is None:
                        raise ValueError(f"Cannot find log value! String given: '{item}'")
                    aiIndex.append(index)
                else:
                    raise ValueError("Invalid item type. Must be int or str.")

        # Step 3: Apply filters if tFilter is provided
        if tFilter:
            aiIndex = self._apply_filters(aiIndex, tFilter)

        if not aiIndex:
            raise ValueError("No log items match the provided criteria.")

        return aiIndex

    def _apply_filters(self, aiIndex, tFilter):
        """
        Apply filters to narrow down the selection.

        Args:
            aiIndex (list): List of log indexes to filter.
            tFilter (dict): Dictionary of filter criteria.

        Returns:
            list: Filtered log indexes.
        """
        abDeleteFinal = [False] * len(aiIndex)  # Track items to delete
        csFilters = list(tFilter.keys())  # Extract filter keys

        for sFilter in csFilters:
            xsValue = tFilter[sFilter]
            if isinstance(xsValue, list):  # Handle list of filter values
                abNoDelete = [False] * len(aiIndex)
                for value in xsValue:
                    abNoDelete = [
                        ab or (self._get_log_field(index, sFilter) == value)
                        for ab, index in zip(abNoDelete, aiIndex)
                    ]
                abDelete = [not x for x in abNoDelete]
            else:  # Single filter value
                abDelete = [
                    self._get_log_field(index, sFilter) != xsValue
                    for index in aiIndex
                ]

            abDeleteFinal = [
                ab1 or ab2 for ab1, ab2 in zip(abDeleteFinal, abDelete)
            ]

        # Remove filtered out indexes
        return [
            index for index, delete in zip(aiIndex, abDeleteFinal) if not delete
        ]

    def _get_log_field(self, index, field):
        """
        Retrieve a field value from tLogValues or tVirtualValues based on index.

        Args:
            index (int): Index of the log item (negative for tVirtualValues).
            field (str): Field name to retrieve.

        Returns:
            str: Value of the specified field.
        """
        if index >= 0:
            return self.tLogValues[index].get(field, None)
        else:
            return self.tVirtualValues[-index - 1].get(field, None)
