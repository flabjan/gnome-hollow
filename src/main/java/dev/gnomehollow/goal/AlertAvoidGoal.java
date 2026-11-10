package dev.gnomehollow.goal;

import dev.gnomehollow.ModSounds;
import dev.gnomehollow.entity.GnomeEntity;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.monster.Monster;

/** Vluchten voor monsters, met een schrikgeluid zodra het begint. */
public class AlertAvoidGoal extends AvoidEntityGoal<Monster> {
	private final GnomeEntity gnome;

	public AlertAvoidGoal(GnomeEntity gnome, float maxDist, double walkSpeed, double sprintSpeed) {
		super(gnome, Monster.class, maxDist, walkSpeed, sprintSpeed);
		this.gnome = gnome;
	}

	@Override
	public void start() {
		super.start();
		this.gnome.voice(ModSounds.ALERT, 1.0F);
	}
}
