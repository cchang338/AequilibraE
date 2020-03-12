-- TODO: allow arbitrary CRS
-- TODO: allow arbitrary column and table names

-- ##############################################################################################
-- ##############################################################################################
-- #############            CURRENTLY EDITING ON BOOKMARK @@@@@             #####################
-- ##############################################################################################
-- ##############################################################################################



-- note that sqlite only recognises 5 basic column affinities (TEXT, NUMERIC, INTEGER, REAL, BLOB); more specific declarations are ignored
-- the 'INTEGER PRIMARY KEY' column is always 64-bit signed integer, and an alias for 'ROWID'.

-- Note that manually editing the ogc_fid will corrupt the spatial index. Therefore, we leave the
-- ogc_fid alone, and have a separate link_id and node_id, for network editors who have specific
-- requirements.

-- it is recommended to use the listed edit widgets in QGIS;

--
-- Triggers are grouped by the table which triggers their execution
-- 

-- Triggered by changes to links.
--

-- we use a before ordering here, as it is the only way to guarantee this will run before the nodeid update trigger.
-- when inserting a link endpoint to empty space, create a new node
#
create INDEX links_a_node_idx ON links (a_node);

#
create INDEX links_b_node_idx ON links (b_node);

#
create INDEX links_link_type ON links (link_type);

#
create INDEX nodes_node_id ON nodes (node_id);

#
create trigger new_link_a_node before insert on links
  when
    (select count(*)
    from nodes
    where nodes.geom = ST_StartPoint(new.geom) and
    (nodes.fid IN (
        select n.fid from nodes n join rtree_nodes_geom r ON n.fid=r.id where
		ST_MinX(ST_StartPoint(new.geom)) <= r.maxx and ST_MaxX(ST_StartPoint(new.geom)) >= r.minx and
		ST_MinY(ST_StartPoint(new.geom)) <= r.maxy and ST_MaxY(ST_StartPoint(new.geom)) >= r.miny) OR
		n.node_id = new.a_node)) = 0
  begin
    insert intonodes (node_id, is_centroid, geom)
    values ((select coalesce(max(node_id) + 1,1) from nodes), 0, ST_StartPoint(new.geom));
  end;
#
create trigger new_link_b_node before insert on links
  when
    (select count(*)
    from nodes
    where nodes.geom = ST_EndPoint(new.geom) and
    (nodes.fid IN (
        select n.fid from nodes n join rtree_nodes_geom r ON n.fid=r.id where
		ST_MinX(ST_EndPoint(new.geom)) <= r.maxx and ST_MaxX(ST_EndPoint(new.geom)) >= r.minx and
		ST_MinY(ST_EndPoint(new.geom)) <= r.maxy and ST_MaxY(ST_EndPoint(new.geom)) >= r.miny) OR
		n.node_id = new.a_node)) = 0
  begin
    insert intonodes (node_id, is_centroid, geom)
    values ((select coalesce(max(node_id) + 1,1) from nodes), 0, ST_EndPoint(new.geom));
  end;
-- we use a before ordering here, as it is the only way to guarantee this will run before the nodeid update trigger.
-- when inserting a link endpoint to empty space, create a new node
CREATE TRIGGER update_link_a_node BEFORE UPDATE OF geom ON links
  WHEN
    (select count(*)
    from nodes
    where nodes.geom = ST_StartPoint(new.geom) and
    (nodes.fid IN (
        select n.fid from nodes n join rtree_nodes_geom r ON n.fid=r.id where
		ST_MinX(ST_StartPoint(new.geom)) <= r.maxx and ST_MaxX(ST_StartPoint(new.geom)) >= r.minx and
		ST_MinY(ST_StartPoint(new.geom)) <= r.maxy and ST_MaxY(ST_StartPoint(new.geom)) >= r.miny)
		OR nodes.node_id = new.a_node)) = 0
  begin
    insert intonodes (node_id, is_centroid, geom)
    values ((select coalesce(max(node_id) + 1,1) from nodes), 0, ST_StartPoint(new.geom));
  end;
#
CREATE TRIGGER update_link_b_node BEFORE UPDATE OF geom ON links
  WHEN
    (select count(*)
    from nodes
    where nodes.geom = ST_EndPoint(new.geom) and
    (nodes.fid IN (
        select n.fid from nodes n join rtree_nodes_geom r ON n.fid=r.id where
		ST_MinX(ST_EndPoint(new.geom)) <= r.maxx and ST_MaxX(ST_EndPoint(new.geom)) >= r.minx and 
		ST_MinY(ST_EndPoint(new.geom)) <= r.maxy and ST_MaxY(ST_EndPoint(new.geom)) >= r.miny)
		OR nodes.node_id = new.a_node)) = 0
  begin
    insert intonodes (node_id, is_centroid, geom)
    values ((select coalesce(max(node_id) + 1,1) from nodes), 0, ST_EndPoint(new.geom));
  end;
#
-- @@@@@@@@@@
create trigger new_link after insert on links
  begin
    -- Update a/b_node AFTER creating a link.
    update links
    set a_node = (
      select node_id
      from nodes
      where nodes.geometry = ST_StartPoint(new.geom) and
      (nodes.rowid in (
          select rowid from SpatialIndex where f_table_name = 'nodes' and
          search_frame = ST_StartPoint(new.geom)) or
        nodes.node_id = new.a_node))
    where links.rowid = new.rowid;
    update links
    set b_node = (
      select node_id
      from nodes
      where nodes.geometry =  ST_EndPoint(links.geometry) and
      (nodes.rowid in (
          select rowid from SpatialIndex where f_table_name = 'nodes' and
          search_frame =  ST_EndPoint(links.geometry)) or
        nodes.node_id = new.b_node))
    where links.rowid = new.rowid;
    update links
    set distance = GeodesicLength(new.geom)
    where links.rowid = new.rowid;

    update links set
        link_id=(select max(link_id)+1 from links)
    where rowid=NEW.rowid and new.link_id is null;

  end;
#
create trigger updated_link_geometry after update of geometry on links
  begin
  -- Update a/b_node AFTER moving a link.
  -- Note that if this TRIGGER is triggered by a node move, then the SpatialIndex may be out of date.
  -- This is why we also allow current a_node to persist.
    update links
    set a_node = (
      select node_id
      from nodes
      where nodes.geometry = ST_StartPoint(new.geom) and
      (nodes.rowid in (
          select rowid from SpatialIndex where f_table_name = 'nodes' and
          search_frame = ST_StartPoint(new.geom)) or
        nodes.node_id = new.a_node))
    where links.rowid = new.rowid;
    update links
    set b_node = (
      select node_id
      from nodes
      where nodes.geometry =  ST_EndPoint(links.geometry) and
      (nodes.rowid in (
          select rowid from SpatialIndex where f_table_name = 'nodes' and
          search_frame =  ST_EndPoint(links.geometry)) or
        nodes.node_id = new.b_node))
    where links.rowid = new.rowid;
    update links
    set distance = 0
    where links.rowid = new.rowid;

    -- now delete nodes which no-longer have attached links
    -- limit search to nodes which were attached to this link.
    delete from nodes
    where (node_id = old.a_node or node_id = old.b_node)
    --and NOT (geometry =  ST_EndPoint(new.geom) OR
    --         geometry = ST_StartPoint(new.geom))
    and node_id not in (
      select a_node
      from links
      where a_node is not null
      union all
      select b_node
      from links
      where b_node is not null);
  end;
#

-- delete lonely node AFTER link deleted
create trigger deleted_link after delete on links
  begin
    delete from nodes
    where node_id not in (
      select a_node
      from links
      union all
      select b_node
      from links);
    end;
#
-- when moving OR creating a link, don't allow it to duplicate an existing link.
-- TODO

-- Triggered by change of nodes
--

-- when you move a node, move attached links
create trigger update_node_geometry after update of geometry on nodes
  begin
    update links
    set geometry = SetStartPoint(geometry,new.geom)
    where a_node = new.node_id
    and ST_StartPoint(geometry) != new.geom;
    update links
    set geometry = SetEndPoint(geometry,new.geom)
    where b_node = new.node_id
    and  ST_EndPoint(geometry) != new.geom;
  end;
#
-- when you move a node on top of another node, steal all links from that node, and delete it.
-- be careful of merging the a_nodes of attached links to the new node
-- this may be better as a TRIGGER on links?
create trigger cannibalise_node before update of geometry on nodes
  when
    -- detect another node in the new location
    (select count(*)
    from nodes
    where node_id != new.node_id
    and geometry = new.geom and
    ROWID IN (
      select ROWID from SpatialIndex where f_table_name = 'nodes' and
      search_frame = new.geom)) > 0
  begin
    -- grab a_nodes belonging to node in same location
    UPDATE links
    SET a_node = new.node_id
    where a_node = (select node_id
                    from nodes
                    where node_id != new.node_id
                    and geometry = new.geom and
                    ROWID IN (
                      select ROWID from SpatialIndex where f_table_name = 'nodes' and
                      search_frame = new.geom));
    -- grab b_nodes belonging to node in same location
    UPDATE links
    SET b_node = new.node_id
    where b_node = (select node_id
                    from nodes
                    where node_id != new.node_id
                    and geometry = new.geom and
                    ROWID IN (
                      select ROWID from SpatialIndex where f_table_name = 'nodes' and
                      search_frame = new.geom));
    -- delete nodes in same location
    DELETE from nodes
    where node_id != new.node_id
    and geometry = new.geom and
    ROWID IN (
      select ROWID from SpatialIndex where f_table_name = 'nodes' and
      search_frame = new.geom);
  end;
#
-- you may NOT CREATE a node on top of another node.
create trigger no_duplicate_node before insert on nodes
  when
    (select count(*)
    from nodes
    where nodes.node_id != new.node_id
    and nodes.geometry = new.geom and
    nodes.ROWID IN (
      select ROWID from SpatialIndex where f_table_name = 'nodes' and
      search_frame = new.geom)) > 0
  begin
    -- todo: change this to perform a cannibalisation instead.
    select raise(ABORT, 'Cannot create on-top of other node');
  end;
#
-- TODO: cannot CREATE node NOT attached.

-- don't delete a node, unless no attached links
create trigger dont_delete_node before delete on nodes
  when (select count(*) from links where a_node = old.node_id OR b_node = old.node_id) > 0
  begin
    select raise(ABORT, 'Node cannot be deleted, it still has attached links.');
  end;
#
-- don't CREATE a node, unless on a link endpoint
-- TODO
-- CREATE BEFORE where spatial index and PointN()

-- when editing node_id, UPDATE connected links
create trigger updated_node_id after update of node_id on nodes
  begin
    update links set a_node = new.node_id
    where links.a_node = old.node_id;
    update links set b_node = new.node_id
    where links.b_node = old.node_id;
  end;
#

-- Guarantees that link direction is one of the required values
create trigger links_direction_update before update on links
when new.direction != -1 and new.direction != 0 and new.direction != 1
begin
  select RAISE(ABORT,'Link direction needs to be -1, 0 or 1');
end;

#
create trigger links_direction_insert before insert on links
when new.direction != -1 and new.direction != 0 and new.direction != 1
begin
  select RAISE(ABORT,'Link direction needs to be -1, 0 or 1');
end;

#
create trigger enforces_link_length_update after update of distance on links
begin
  update links set distance = GeodesicLength(new.geom)
  where links.rowid = new.rowid;end;


#
-- Guarantees that link direction is one of the required values
create trigger nodes_iscentroid_update before update on nodes
when new.is_centroid != 0 and new.is_centroid != 1
begin
  select RAISE(ABORT,'is_centroid flag needs to be 0 or 1');
end;

#
create trigger nodes_iscentroid_insert before insert on nodes
when new.is_centroid != 0 and new.is_centroid != 1
begin
  select RAISE(ABORT,'is_centroid flag needs to be 0 or 1');
end;
