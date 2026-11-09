package dev.gnomehollow.client;

import dev.gnomehollow.GnomeHollow;
import dev.gnomehollow.entity.GnomeEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;
import software.bernie.geckolib.renderer.base.GeoRenderState;

/**
 * Model:      assets/gnomehollow/geckolib/models/entity/<naam>.geo.json
 * Animaties:  assets/gnomehollow/geckolib/animations/entity/<naam>.animation.json
 * Texture:    assets/gnomehollow/textures/entity/<naam>.png
 */
public class GnomeRenderer<R extends LivingEntityRenderState & GeoRenderState> extends GeoEntityRenderer<GnomeEntity, R> {
	public GnomeRenderer(EntityRendererProvider.Context context, String assetName) {
		super(context, new DefaultedEntityGeoModel<>(GnomeHollow.id(assetName)));
	}
}
