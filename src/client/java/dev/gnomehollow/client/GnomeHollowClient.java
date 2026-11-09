package dev.gnomehollow.client;

import dev.gnomehollow.ModEntities;
import dev.gnomehollow.entity.Profession;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

public final class GnomeHollowClient implements ClientModInitializer {
	@Override
	public void onInitializeClient() {
		for (Profession p : Profession.values()) {
			String asset = p.entityName();
			EntityRendererRegistry.register(ModEntities.TYPES.get(p), ctx -> new GnomeRenderer<>(ctx, asset));
		}
	}
}
