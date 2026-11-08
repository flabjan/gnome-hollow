package dev.gnomehollow.entity;

import dev.gnomehollow.ModSounds;
import dev.gnomehollow.goal.AlertAvoidGoal;
import dev.gnomehollow.goal.BuildGoal;
import dev.gnomehollow.goal.FarmGoal;
import dev.gnomehollow.goal.FishGoal;
import dev.gnomehollow.goal.HealerBrewGoal;
import dev.gnomehollow.goal.MusicGoal;
import dev.gnomehollow.goal.NightHomeGoal;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.PanicGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.goal.target.HurtByTargetGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Monster;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.storage.ValueInput;
import net.minecraft.world.level.storage.ValueOutput;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animatable.manager.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * Eén klasse voor alle gnomes. Het beroep volgt uit het EntityType (gnome_healer, gnome_warrior, ...),
 * zodat elk beroep een eigen model/texture kan krijgen zonder gesynchroniseerde data.
 */
public class GnomeEntity extends PathfinderMob implements GeoEntity {
	private static final RawAnimation IDLE = RawAnimation.begin().thenLoop("animation.gnome.idle");
	private static final RawAnimation WALK = RawAnimation.begin().thenLoop("animation.gnome.walk");
	private static final RawAnimation ATTACK = RawAnimation.begin().thenPlay("animation.gnome.attack");
	private static final RawAnimation WORK = RawAnimation.begin().thenLoop("animation.gnome.work");
	private static final RawAnimation FISH = RawAnimation.begin().thenLoop("animation.gnome.fish");
	private static final RawAnimation PLAY = RawAnimation.begin().thenLoop("animation.gnome.play");

	private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);
	private boolean homeSet;
	private BlockPos homePos;
	private int built;
	private boolean playingMusic;
	private int greetCooldown = 100;

	public GnomeEntity(EntityType<? extends GnomeEntity> type, Level level) {
		super(type, level);
		this.setPersistenceRequired();
	}

	public static AttributeSupplier.Builder createGnomeAttributes(Profession p) {
		boolean warrior = p == Profession.WARRIOR;
		return Mob.createMobAttributes()
				.add(Attributes.MAX_HEALTH, warrior ? 30.0 : 16.0)
				.add(Attributes.MOVEMENT_SPEED, 0.27)
				.add(Attributes.ATTACK_DAMAGE, warrior ? 5.0 : 1.0)
				.add(Attributes.FOLLOW_RANGE, 24.0)
				.add(Attributes.KNOCKBACK_RESISTANCE, warrior ? 0.3 : 0.0);
	}

	public Profession profession() {
		return Profession.fromType(this.getType());
	}

	@Override
	protected void registerGoals() {
		Profession p = Profession.fromType(this.getType());

		this.goalSelector.addGoal(0, new FloatGoal(this));
		this.targetSelector.addGoal(1, new HurtByTargetGoal(this).setAlertOthers());

		if (p == Profession.WARRIOR) {
			this.goalSelector.addGoal(1, new MeleeAttackGoal(this, 1.15, true));
			this.targetSelector.addGoal(2, new NearestAttackableTargetGoal<>(this, Monster.class, true));
		} else {
			this.goalSelector.addGoal(1, new PanicGoal(this, 1.4));
			this.goalSelector.addGoal(2, new AlertAvoidGoal(this, 8.0F, 0.8, 1.1));
		}

		switch (p) {
			case FISHERMAN -> this.goalSelector.addGoal(3, new FishGoal(this));
			case HEALER -> this.goalSelector.addGoal(3, new HealerBrewGoal(this));
			case FARMER -> this.goalSelector.addGoal(3, new FarmGoal(this));
			case BUILDER -> this.goalSelector.addGoal(3, new BuildGoal(this));
			case NITWIT -> this.goalSelector.addGoal(3, new MusicGoal(this));
			case WARRIOR -> { }
		}

		if (p != Profession.WARRIOR) {
			this.goalSelector.addGoal(4, new NightHomeGoal(this));
		}
		this.goalSelector.addGoal(5, new WaterAvoidingRandomStrollGoal(this, 0.6));
		this.goalSelector.addGoal(6, new LookAtPlayerGoal(this, Player.class, 6.0F));
		this.goalSelector.addGoal(7, new RandomLookAroundGoal(this));
	}

	@Override
	public void tick() {
		super.tick();
		if (!this.level().isClientSide() && !this.homeSet) {
			this.homeSet = true;
			this.homePos = this.blockPosition();
			this.restrictTo(this.homePos, 32);
		}
	}

	@Override
	public void aiStep() {
		super.aiStep();
		// Healer: geneest gewonde spelers, dorpelingen, gnomes en golems in de buurt.
		if (!this.level().isClientSide() && this.level() instanceof ServerLevel server
				&& this.profession() == Profession.HEALER && this.tickCount % 40 == 0 && this.isAlive()) {
			List<LivingEntity> hurt = server.getEntitiesOfClass(LivingEntity.class, this.getBoundingBox().inflate(6.0),
					e -> e != this && e.isAlive() && e.getHealth() < e.getMaxHealth() - 2.0F
							&& (e instanceof Player || e instanceof GnomeEntity || e.getType() == EntityType.VILLAGER || e.getType() == EntityType.IRON_GOLEM));
			if (!hurt.isEmpty()) {
				LivingEntity patient = hurt.get(0);
				patient.heal(4.0F);
				server.sendParticles(ParticleTypes.HEART, patient.getX(), patient.getY() + patient.getBbHeight() + 0.2,
						patient.getZ(), 5, 0.3, 0.2, 0.3, 0.0);
				server.playSound(null, patient.blockPosition(), SoundEvents.AMETHYST_BLOCK_CHIME, SoundSource.NEUTRAL, 1.0F, 1.4F);
				this.triggerAnim("action", "work");
				this.voice(ModSounds.HEAL, 1.0F);
			}
		}
		// Groeten: een vriendelijk "hii-hii!" als een speler dichtbij komt.
		if (!this.level().isClientSide() && this.isAlive()) {
			if (this.greetCooldown > 0) {
				this.greetCooldown--;
			} else if (this.tickCount % 20 == 0 && this.isWorkTime()) {
				Player p = this.level().getNearestPlayer(this, 4.0);
				if (p != null && !p.isSpectator() && this.hasLineOfSight(p)) {
					this.voice(ModSounds.GREET, 1.0F);
					this.greetCooldown = 1200 + this.random.nextInt(600);
				}
			}
		}
	}

	@Override
	public void swing(InteractionHand hand) {
		if (!this.level().isClientSide()) {
			this.triggerAnim("action", "attack");
			if (this.profession() == Profession.WARRIOR && this.random.nextInt(3) == 0) {
				this.voice(ModSounds.ATTACK, 1.0F);
			}
		}
		super.swing(hand);
	}

	// ---- helpers voor goals ----

	public boolean isWorkTime() {
		return this.level().isBrightOutside();
	}

	public BlockPos home() {
		return this.homePos;
	}

	public int builtCount() {
		return this.built;
	}

	public void addBuilt() {
		this.built++;
	}

	public boolean isPlayingMusic() {
		return this.playingMusic;
	}

	public void setPlayingMusic(boolean playing) {
		this.playingMusic = playing;
	}

	public void startAnim(String name) {
		if (!this.level().isClientSide()) {
			this.triggerAnim("action", name);
		}
	}

	public void stopAnim() {
		if (!this.level().isClientSide()) {
			this.stopTriggeredAnimation("action", null);
		}
	}

	// ---- opslaan ----

	@Override
	protected void addAdditionalSaveData(ValueOutput output) {
		super.addAdditionalSaveData(output);
		output.putInt("Built", this.built);
	}

	@Override
	protected void readAdditionalSaveData(ValueInput input) {
		super.readAdditionalSaveData(input);
		this.built = input.getIntOr("Built", 0);
	}

	@Override
	public boolean removeWhenFarAway(double distanceToClosestPlayer) {
		return false;
	}

	// ---- geluiden (eigen kabouterstem, zie ModSounds) ----

	/** Basis-toonhoogte per beroep: de krijger is wat dieper, de nitwit het schelst. */
	private float voicePitch() {
		return switch (this.profession()) {
			case WARRIOR -> 0.9F;
			case BUILDER -> 0.85F;
			case FISHERMAN -> 0.95F;
			case FARMER -> 1.0F;
			case HEALER -> 1.1F;
			case NITWIT -> 1.2F;
		};
	}

	/** Speelt een stemgeluid met een lichte willekeurige variatie af (alleen server-kant aanroepen). */
	public void voice(SoundEvent sound, float volume) {
		if (sound == null || this.level().isClientSide()) return;
		this.playSound(sound, volume, this.voicePitch() + (this.random.nextFloat() - 0.5F) * 0.12F);
	}

	@Override
	protected SoundEvent getAmbientSound() {
		// 's Nachts bij huis: snurken in plaats van brabbelen.
		if (!this.isWorkTime() && this.homePos != null
				&& this.distanceToSqr(this.homePos.getX() + 0.5, this.homePos.getY(), this.homePos.getZ() + 0.5) < 36.0) {
			return ModSounds.SNORE;
		}
		return ModSounds.AMBIENT;
	}

	@Override
	protected SoundEvent getHurtSound(DamageSource source) {
		return ModSounds.HURT;
	}

	@Override
	protected SoundEvent getDeathSound() {
		return ModSounds.DEATH;
	}

	@Override
	protected void playStepSound(BlockPos pos, BlockState state) {
		this.playSound(ModSounds.STEP, 0.35F, 0.9F + this.random.nextFloat() * 0.3F);
	}

	@Override
	public void setTarget(LivingEntity target) {
		boolean newTarget = target != null && this.getTarget() == null;
		super.setTarget(target);
		if (newTarget && this.profession() == Profession.WARRIOR) {
			this.voice(ModSounds.ATTACK, 1.0F);
		}
	}

	/** Rechtsklik: overdag een vrolijke "ja!", 's nachts een chagrijnig "nee". */
	@Override
	public InteractionResult mobInteract(Player player, InteractionHand hand) {
		if (!this.level().isClientSide()) {
			this.getLookControl().setLookAt(player);
			this.voice(this.isWorkTime() ? ModSounds.YES : ModSounds.NO, 1.0F);
		}
		return InteractionResult.SUCCESS;
	}

	// ---- GeckoLib ----

	@Override
	public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
		controllers.add(new AnimationController<GnomeEntity>("move", 4,
				state -> state.isMoving() ? state.setAndContinue(WALK) : state.setAndContinue(IDLE)));
		controllers.add(new AnimationController<GnomeEntity>("action", 2, state -> PlayState.STOP)
				.triggerableAnim("attack", ATTACK)
				.triggerableAnim("work", WORK)
				.triggerableAnim("fish", FISH)
				.triggerableAnim("play", PLAY));
	}

	@Override
	public AnimatableInstanceCache getAnimatableInstanceCache() {
		return this.cache;
	}
}
