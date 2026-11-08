package dev.gnomehollow.client;

import dev.gnomehollow.GnomeHollow;
import dev.gnomehollow.entity.GnomeEntity;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.LivingEntityRenderState;
import com.geckolib.model.DefaultedEntityGeoModel;
import com.geckolib.renderer.GeoEntityRenderer;

/**
 * Model:      assets/gnomehollow/geckolib/models/entity/<naam>.geo.json
 * Animaties:  assets/gnomehollow/geckolib/animations/entity/<naam>.animation.json
 * Texture:    assets/gnomehollow/textures/entity/<naam>.png
 */
public class GnomeRenderer extends GeoEntityRenderer<GnomeEntity, LivingEntityRenderState> {
	public GnomeRenderer(EntityRendererProvider.Context context, String assetName) {
		super(context, new DefaultedEntityGeoModel<>(GnomeHollow.id(assetName)));
	}
}
