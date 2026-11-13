package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.List;
import java.util.UUID;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;

/** Even kletsen met een vriend of een buur. Wie uitgenodigd wordt, blijft staan en luistert/praat terug. Zo ontstaan vriendschappen. */
public class ChatGoal extends ActivityGoal {
	private GnomeEntity partner;
	private boolean listener;

	public ChatGoal(GnomeEntity gnome) {
		super(gnome, 400);
	}

	@Override
	protected boolean allowed() {
		return this.gnome.canLeisure() && (this.listener || this.gnome.chatInviter() != null || this.gnome.hasVillage());
	}

	@Override
	protected int nextCooldown() {
		return 600 + this.gnome.getRandom().nextInt(1200);
	}

	@Override
	protected boolean needsWalk() {
		return !this.listener;
	}

	@Override
	protected boolean choose(ServerLevel level) {
		this.listener = false;
		GnomeEntity inviter = this.gnome.chatInviter();
		if (inviter != null) {
			this.partner = inviter;
			this.listener = true;
			this.dest = null;
			this.duration = 260;
			return true;
		}
		var rnd = this.gnome.getRandom();
		boolean wantsToChat = this.gnome.favorite() == 3 || rnd.nextInt(3) == 0;
		if (!wantsToChat || !this.gnome.busyLeisureChance()) return false;
		GnomeEntity target = null;
		UUID fid = this.gnome.friend();
		if (fid != null) {
			Entity e = level.getEntity(fid);
			if (e instanceof GnomeEntity f && f.isAlive() && f.distanceToSqr(this.gnome) < 40.0 * 40.0 && f.canLeisure()) target = f;
		}
		if (target == null) {
			List<GnomeEntity> near = level.getEntitiesOfClass(GnomeEntity.class, this.gnome.getBoundingBox().inflate(16.0, 4.0, 16.0),
					g -> g != this.gnome && g.isAlive() && g.canLeisure() && g.chatInviter() == null);
			if (near.isEmpty()) return false;
			target = near.get(rnd.nextInt(near.size()));
		}
		this.partner = target;
		this.dest = target.blockPosition();
		this.duration = 260 + rnd.nextInt(200);
		return true;
	}

	@Override
	protected void refreshDest() {
		if (this.partner != null) this.dest = this.partner.blockPosition();
	}

	@Override
	protected double arriveDist() {
		return 2.6;
	}

	@Override
	protected void onArrive(ServerLevel level) {
		if (!this.listener && this.partner != null) {
			this.partner.inviteToChat(this.gnome, this.duration + 60);
			this.gnome.voice(dev.gnomehollow.ModSounds.AMBIENT, 0.6F);
		}
	}

	@Override
	protected void during(ServerLevel level) {
		if (this.partner == null || !this.partner.isAlive()) {
			this.ticks = this.duration;
			return;
		}
		if (this.gnome.tickCount % 10 == 0) this.gnome.getLookControl().setLookAt(this.partner, 30.0F, 30.0F);
		int phase = this.ticks % 80;
		if (phase == (this.listener ? 40 : 0)) this.gnome.oneShot("talk");
	}

	@Override
	protected void onEnd(ServerLevel level) {
		if (this.partner != null && this.arrived && !this.listener) {
			this.gnome.chattedWith(this.partner);
			this.partner.clearInvite();
		}
		if (this.listener) this.gnome.clearInvite();
		this.gnome.stopAnim();
		this.partner = null;
		this.listener = false;
	}
}
