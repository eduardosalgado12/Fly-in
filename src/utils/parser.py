from src.models import ZoneType, Zone, Graph, Connection, StartHub, EndHub


class ParserError(Exception):
    """Raised when the map file has an invalid or malformed line."""
    ...


class Parser:
    """Parses a Fly-in map file into a Graph and drone count."""

    def __init__(self) -> None:
        """Initializes an empty parser, with no graph parsed yet."""
        self.graph = Graph()
        self.nb_drones: int = 0
        self.current_line: int = 0

    def parse(self, file_map: str) -> None:
        """Reads the map file and populates self.graph and self.nb_drones.

        Args:
            file_map: Path to the map file to parse.

        Raises:
            ParserError: If any line of the file is invalid or malformed.
        """
        with open(file_map, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for i in range(0, len(lines)):
                nbr_line = i + 1
                line = lines[i].strip()
                self.current_line = nbr_line
                self._parse_line(line)

        if self.graph.start is None:
            raise ParserError("Missing required start_hub zone")
        if self.graph.end is None:
            raise ParserError("Missing required end_hub zone")

    def _parse_line(self, line: str) -> None:
        """Identifies the line type and delegates to the right handler.

        Args:
            line: A single, already-stripped line from the map file.

        Raises:
            ParserError: If the line does not match any known format.
        """
        if line == "" or line.startswith("#"):
            return

        if line.startswith("nb_drones:"):
            self._parse_nb_drones(line.removeprefix("nb_drones: "))
        elif line.startswith("start_hub:"):
            self._parse_zone(line.removeprefix("start_hub: "), is_start=True)
        elif line.startswith("end_hub:"):
            self._parse_zone(line.removeprefix("end_hub: "), is_end=True)
        elif line.startswith("hub:"):
            self._parse_zone(line.removeprefix("hub: "))
        elif line.startswith("connection: "):
            self._parse_connection(line.removeprefix("connection: "))
        else:
            raise ParserError(
                f"Line {self.current_line}: unrecognized line format"
            )

    def _parse_nb_drones(self, line: str) -> None:
        """Parses the 'nb_drones: <positive_integer>' line.

        Args:
            line: The value part of the line, after the 'nb_drones:' prefix.

        Raises:
            ParserError: If the value is not a positive integer.
        """
        try:
            nb_drones = int(line)
        except ValueError:
            raise ParserError(
                f"Line {self.current_line}: nb_drones must be integer")

        if nb_drones <= 0:
            raise ParserError(
                f"Line {self.current_line}: nb_drones must be positive")

        self.nb_drones = nb_drones

    def _parse_metadata(self, block: str) -> dict[str, str]:
        """Parses a '[key=value key2=value2]' block into a dict.

        Args:
            block: The metadata block, e.g. "zone=priority color=green]".

        Returns:
            A dict mapping each metadata key to its raw string value.

        Raises:
            ParserError: If any pair in the block is not in 'key=value' form.
        """
        metadata: dict[str, str] = {}

        for pair in block.strip("]").split():
            if "=" not in pair:
                raise ParserError(
                    f"Line {self.current_line}: invalid metadata '{pair}'"
                )
            key, value = pair.split("=", 1)
            metadata[key] = value

        return metadata

    def _parse_zone(self, line: str, is_start: bool = False,
                    is_end: bool = False) -> None:
        """Parses a 'hub:'/'start_hub:'/'end_hub:' line into a zone.

        Args:
            line: The value part of the line, after its prefix, e.g.
                "roof1 3 4 [zone=restricted color=red]".
            is_start: Whether this line declares the start zone.
            is_end: Whether this line declares the end zone.

        Raises:
            ParserError: If the zone name, coordinates or metadata are
                invalid, the name is already used, or a duplicate
                start/end zone is declared.
        """
        if "[" in line:
            zone_str, metadata_block = line.split("[", 1)
            metadata = self._parse_metadata(metadata_block)
        else:
            zone_str = line
            metadata = {}

        parts = zone_str.split()
        try:
            name = parts[0]
            x_str = parts[1]
            y_str = parts[2]
        except IndexError:
            raise ParserError(
                f"Line {self.current_line}: zone line must have a name, "
                f"x and y"
            )

        if "-" in name or " " in name:
            raise ParserError(
                f"Line {self.current_line}: zone names can't contain "
                f"dashes or spaces"
            )

        if name in self.graph.zones:
            raise ParserError(
                f"Line {self.current_line}: name need to be unique")

        try:
            x = int(x_str)
            y = int(y_str)
        except ValueError:
            raise ParserError(
                f"Line {self.current_line}: x and y must be integer")

        zone_type_str = metadata.get("zone", "normal")
        try:
            zone_type = ZoneType(zone_type_str)
        except ValueError:
            raise ParserError(
                f"Line {self.current_line}: invalid zone type {zone_type}"
                )

        color = metadata.get("color")

        max_drones_str = metadata.get("max_drones", "1")
        try:
            max_drones = int(max_drones_str)
        except ValueError:
            raise ParserError(
                f"Line {self.current_line}: max_drones must be an integer"
                )
        if max_drones <= 0:
            raise ParserError(
                f"Line {self.current_line}: max_drones must be positive"
                )

        if is_start:
            if self.graph.start is None:
                self.graph.add_zone(StartHub(name, x, y, color=color))
            else:
                raise ParserError(
                    f"Line {self.current_line}: only one start_hub is allowed")
        elif is_end:
            if self.graph.end is None:
                self.graph.add_zone(EndHub(name, x, y, color=color))
            else:
                raise ParserError(
                    f"Line {self.current_line}: only one end_hub is allowed")
        else:
            self.graph.add_zone(Zone(name, x, y, zone_type, color, max_drones))

    def _parse_connection(self, line: str) -> None:
        """Parses a 'connection: <zone1>-<zone2> [metadata]' line.

        Args:
            line: The value part of the line, after the 'connection:'
                prefix, e.g. "roof1-corridorA [max_link_capacity=2]".

        Raises:
            ParserError: If `max_link_capacity` is invalid, or either
                endpoint zone is unknown (raised by `Graph.add_connection`).
        """
        if "[" in line:
            connection_str, metadata_block = line.split("[", 1)
            metadata = self._parse_metadata(metadata_block)
        else:
            connection_str = line
            metadata = {}

        parts = connection_str.strip().split("-", 1)
        try:
            zone1 = parts[0].strip()
            zone2 = parts[1].strip()
        except IndexError:
            raise ParserError(
                f"Line {self.current_line}: connection must be in the "
                f"form <zone1>-<zone2>"
            )

        max_link_capacity_str = metadata.get("max_link_capacity", "1")
        try:
            max_link_capacity = int(max_link_capacity_str)
        except ValueError:
            raise ParserError(
                f"Line {self.current_line}: "
                f"max_link_capacity must be an integer"
            )
        if max_link_capacity <= 0:
            raise ParserError(
                f"Line {self.current_line}: max_link_capacity must be positive"
            )

        try:
            self.graph.add_connection(
                Connection(zone1, zone2, max_link_capacity))
        except ValueError as e:
            raise ParserError(f"Line {self.current_line}: {e}")
