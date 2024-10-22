
/**
 * An enumeration for the different states that the loading, creation, updating, or deletion of a resource can be in.
 */
export enum ResourceState {

    /**
     * The resource hasn't been loaded, created, updated, or deleted yet.
     */
    Pending = 'pending',

    /**
     * The resource is currently being loaded.
     */
    Loading = 'loading',

    /**
     * The resource is currently being saved.
     */
    Saving = 'saving',

    /**
     * The resource is currently being created.
     */
    Creating = 'creating',

    /**
     * The resource is currently being updated.
     */
    Updating = 'updating',

    /**
     * The resource is currently being deleted.
     */
    Deleting = 'deleting',

    /**
     * The resource was successfully loaded, created, updated, or deleted.
     */
    Finished = 'finished',

    /**
     * An error occurred while loading, creating, updating, or deleting the resource.
     */
    Failed = 'failed',
  }
