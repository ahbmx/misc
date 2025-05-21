# View current zoning configuration
zoneshow
cfgshow

# View active zoning configuration (enabled zones)
zoneshow --active
cfgactshow

# Create a new zone
zonecreate "zone_name", "member1; member2"

# Add members to existing zone
zoneadd "zone_name", "additional_member"

# Remove members from zone
zoneremove "zone_name", "member_to_remove"

# Create a new configuration
cfgcreate "cfg_name", "zone_name1; zone_name2"

# Add zone to configuration
cfgadd "cfg_name", "zone_name"

# Remove zone from configuration
cfgremove "cfg_name", "zone_name"

# Enable/activate a configuration
cfgenable "cfg_name"

# Disable a configuration (returns to default zone)
cfgdisable

# Delete a zone
zonedelete "zone_name"

# Delete a configuration
cfgdelete "cfg_name"

# Save zoning configuration
cfgsave