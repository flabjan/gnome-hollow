package dev.gnomehollow;

import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.entity.Profession;
import java.util.EnumMap;
import java.util.Map;
import net.fabricmc.fabric.api.object.builder.v1.entity.FabricDefaultAttributeRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;

public final class ModEntities {
	public static final Map<Profession, EntityType<GnomeEntity>> TYPES = new EnumMap<>(Profession.class);

	private ModEntities() {}

	public static void init() {
		for (Profession p : Profession.values()) {
			ResourceKey<EntityType<?>> key = ResourceKey.create(Registries.ENTITY_TYPE, GnomeHollow.id(p.entityName()));
			EntityType<GnomeEntity> type = EntityType.Builder.of(GnomeEntity::new, MobCategory.CREATURE)
					.sized(0.5f, 1.0f)
					.eyeHeight(0.8f)
					.clientTrackingRange(10)
					.build(key);
			Registry.register(BuiltInRegistries.ENTITY_TYPE, key, type);
			FabricDefaultAttributeRegistry.register(type, GnomeEntity.createGnomeAttributes(p));
			TYPES.put(p, type);
		}
	}
}
