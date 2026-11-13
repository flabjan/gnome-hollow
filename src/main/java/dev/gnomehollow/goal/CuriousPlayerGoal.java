package dev.gnomehollow.goal;

import dev.gnomehollow.ModSounds;
import dev.gnomehollow.entity.GnomeEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;

/** Nieuwsgierigheid: een gnome loopt naar een speler toe. Bekende spelers krijgen een zwaai (herkend), nieuwe een begroeting. Geen reputatiesysteem. */
public class CuriousPlayerGoal extends ActivityGoal {
	private Player player;
	private boolean known;

	public CuriousPlayerGoal(GnomeEntity gnome) {
		super(gnome, 300);
	}

	@Override
	protected int nextCooldown() {
		return 3000 + this.gnome.getRandom().nextInt(3000);
	}

	@Override
	protected boolean choose(ServerLevel level) {
		Player p = level.getNearestPlayer(this.gnome, 9.0);
		if (p == null || p.isSpectator() || !this.gnome.hasLineOfSight(p) || p.isCrouching()) return false;
		if (this.gnome.getRandom().nextInt(3) != 0) return false;
		this.player = p;
		this.known = this.gnome.knows(p.getUUID());
		this.dest = p.blockPosition();
		this.duration = 120;
		return true;
	}

	@Override
	protected void refreshDest() {
		if (this.player != null) this.dest = this.player.blockPosition();
	}

	@Override
	protected double arriveDist() {
		return 3.2;
	}

	@Override
	protected void onArrive(ServerLevel level) {
		this.gnome.getLookControl().setLookAt(this.player, 30.0F, 30.0F);
		this.gnome.voice(ModSounds.GREET, 1.0F);
		if (this.known) {
			this.gnome.oneShot("wave");
			level.sendParticles(ParticleTypes.HAPPY_VILLAGER, this.gnome.getX(), this.gnome.getY() + 1.3, this.gnome.getZ(), 4, 0.3, 0.2, 0.3, 0.0);
		} else {
			this.gnome.oneShot("talk");
			this.gnome.learn(this.player.getUUID());
		}
	}

	@Override
	protected void during(ServerLevel level) {
		if (this.gnome.tickCount % 10 == 0 && this.player != null) this.gnome.getLookControl().setLookAt(this.player, 30.0F, 30.0F);
	}

	@Override
	protected void onEnd(ServerLevel level) {
		this.player = null;
	}
}
